import json
import sqlite3
import sys
from datetime import datetime
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = "students.db"

def get_time():
    return datetime.now().isoformat(timespec="seconds")

def query_students(name=None, grade=None):
    """根据姓名或年级查学生。都为 None 时返回所有学生(转成 dict 列表,便于 JSON 序列化)。"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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
                        "description": "年级,必须传这三个值之一。",
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
