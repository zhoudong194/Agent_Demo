import json
import sqlite3
import sys
from datetime import datetime
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = "students.db"

def get_time():
    return datetime.now().isoformat(timespec="seconds")

def query_students(name=None, grade=None, return_year = None):
    """根据姓名或年级查学生。都为 None 时返回所有学生(转成 dict 列表,便于 JSON 序列化),return_year为None时返回所有年级的学生，否则返回指定年级的学生"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if(return_year is not None):
        grade = f"{return_year}级"

    sql = "SELECT * FROM students"
    params = []
    conditions = []

    if name is not None:
        conditions.append("name = ?")
        params.append(name)
    if grade is not None:
        conditions.append("grade = ?")
        params.append(grade)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    # sql += "LIMIT ? OFFSET ?"
    # limit = 20

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


# 函数到 tool 的映射
func_list = {
    "get_time": get_time,
    "query_students": query_students,
}

tools_description = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前日期时间,用于回答涉及'今年/去年/前年'类相对时间问题。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_students",
            "description": (
                "按姓名或年级查询学生信息。两个参数都不传时返回全部学生。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name":  {"type": "string", "description": "学生姓名,精确匹配。"},
                    "grade": {
                        "type": "string",
                        "enum": ["2022级", "2023级", "2024级"],
                        "description": "年级，如'2024级'。若return_year不为None，则返回指定年级的学生。",
                    },
                    "return_year": {
                        "type": "integer",
                        "description": "入学年份数字(如 2024),会自动转成 grade='2024级,用于返回指定年级的学生。",
                    },
                },
                "required": [],
            },
        },
    },
]

client = OpenAI(
    api_key="sk-96c0a475965841fd9b6b95276e5b68ba",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

SYSTEM_PROMPT = (
    "你是一个私人助理。请严格按 ReAct 风格思考，在每次对话中都要添加：主人你好."
    "当你需要查询学生信息时，请使用工具;涉及'今年/去年/前年'等相对时间时,先调 get_time 拿到 ISO 时间后传入return_year参数，如'2024'。"
)


while True:
    text = input("你:")
    if not text.strip():
        continue
    if text == "exit":
        break

    history = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": text},
    ]

    for turn in range(5):
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=history,
            tools=tools_description,
            tool_choice="auto",
            temperature=0.0,
        )

        # 里面有content 和 tool_calls
        curr_msg = response.choices[0].message
        # content是模型的第n轮输出，思考过程，留着准备存入history
        content = curr_msg.content or ""
        # 工具列表 看是否本轮要调用工具
        tool_calls = curr_msg.tool_calls or []

        print(f"\n 第{turn + 1}轮思考")
        print(content)

        assistant_dict = {"role": "assistant", "content": content}
        if tool_calls:
            assistant_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ]

        # 是否有tool拼接进来，组成本轮的assistant消息
        history.append(assistant_dict)

        # 本轮没有工具调用了，break
        if not tool_calls:
            break

        # 从列表中依次取出工具
        for tc in tool_calls:
            name = tc.function.name
            raw_args = tc.function.arguments or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}
            print("tool_name: "+ name + "\n")
            print(f"tool_json: {args}\n")

            # 找到函数的映射
            func = func_list[name]
            # **args 字典解包，把参数字典拆成关键字参数传给函数，执行函数
            result = func(**args)

            #将工具返回的额JSON字符串作为observation
            observation = json.dumps(result, ensure_ascii=False, default=str)
            print(f"Observation[{name}]: {observation}")

            history.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": observation,
            })

    print()

# 你:查询前年入学的学生
#
#  第1轮思考
# Thought: 需要知道“前年”是哪一年，才能确定对应的学生年级（如2022级表示2022年入学）。因此先调用 get_time 获取当前日期时间，从而推算出前年。
#
# tool_name: get_time
#
# tool_json: {}
#
# Observation[get_time]: "2026-08-06T09:53:49"
#
#  第2轮思考
# Thought: 当前时间是2026年8月6日，因此前年是2024年。对应入学年级为“2024级”。现在调用 query_students 查询2024级所有学生。
#
#
# tool_name: query_students
#
# tool_json: {'grade': '2024级'}
#
# Observation[query_students]: [[1, "2024001", "张三", 20, "男", "计算机科学与技术", "2024级", "计科1班", 3.85, "zhangsan@school.edu", "13800000001", "2024-09-01"], [2, "2024002", "李四", 19, "女", "软件工程", "2024级", "软工2班", 3.72, "lisi@school.edu", "13800000002", "2024-09-01"], [6, "2024006", "孙八", 19, "女", "软件工程", "2024级", "软工1班", 3.88, "sunba@school.edu", "13800000006", "2024-09-01"], [9, "2024009", "郑十一", 19, "男", "数据科学", "2024级", "数据2班", 3.55, "zhengshiyi@school.edu", "13800000009", "2024-09-01"]]
#
#  第3轮思考
# 主人你好! 前年（2024年）入学的学生有：
#
# - 张三，学号2024001，计算机科学与技术专业，计科1班，GPA 3.85
# - 李四，学号2024002，软件工程专业，软工2班，GPA 3.72
# - 孙八，学号2024006，软件工程专业，软工1班，GPA 3.88
# - 郑十一，学号2024009，数据科学专业，数据2班，GPA 3.55
