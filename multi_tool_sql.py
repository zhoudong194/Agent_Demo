import json
import sqlite3
from datetime import datetime
from openai import OpenAI

DB_PATH = "students.db"

def get_time():
    return datetime.now()


def query_students(name=None):
    """根据姓名查学生。name 为 None 时返回所有学生。"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sql = "SELECT * FROM students"
    params = []

    if name is not None:
        sql += " WHERE name = ?"
        params.append(name)

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


# 函数到 tool 的映射
func_list = {
    "get_time": get_time,
    "query_students": query_students,
}

# 工具描述
tool_description = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前时间,不需要参数",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_students",
            "description": "查询学生信息数据库。不传参数返回所有学生,传 name 按姓名精确查询。",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "学生姓名,例如 张三",
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

history = [
    {
        "role": "system",
        "content": "你是一个严肃的私人助理,你在回答我的问题前加一句:\"主人你好!\"。你需要根据 tools 描述调用我编写的工具。",
    }
]

while True:
    text = input("你:")

    if text.isspace():
        continue
    if text == "exit":
        break
    history.append({"role": "user", "content": text})

    response = client.chat.completions.create(
        model="qwen-plus",
        stream=False,
        messages=history,
        temperature=0.8,
        tools=tool_description,
    )

    curr_msg = response.choices[0].message
    history.append(curr_msg.model_dump())

    if curr_msg.tool_calls:
        tool_call = curr_msg.tool_calls[0]
        tool_name = tool_call.function.name
        print("模型调用的工具为:" + tool_name)

        args = json.loads(tool_call.function.arguments)
        func = func_list[tool_name]
        result = func(**args)
        print("result:" + json.dumps(result, ensure_ascii=False))

        tool_msg = {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result, ensure_ascii=False),
        }
        history.append(tool_msg)

        final_response = client.chat.completions.create(
            model="qwen-plus",
            stream=False,
            messages=history,
            temperature=0.8,
            tools=tool_description,
        )

        answer = final_response.choices[0].message.content
        print("AI:" + answer)
        history.append({"role": "assistant", "content": answer})
    else:
        final_answer = curr_msg.content
        print("AI:", final_answer)
        history.append({"role": "assistant", "content": final_answer})


# 你:张三成绩如何
# 模型调用的工具为:query_students
# result:[[1, "2024001", "张三", 20, "男", "计算机科学与技术", "2024级", "计科1班", 3.85, "zhangsan@school.edu", "13800000001", "2024-09-01"]]
# AI:张三的成绩绩点为3.85。
# 你:其他学生的信息
# 模型调用的工具为:query_students
# result:[[1, "2024001", "张三", 20, "男", "计算机科学与技术", "2024级", "计科1班", 3.85, "zhangsan@school.edu", "13800000001", "2024-09-01"], [2, "2024002", "李四", 19, "女", "软件工程", "2024级", "软工2班", 3.72, "lisi@school.edu", "13800000002", "2024-09-01"], [3, "2024003", "王五", 21, "男", "人工智能", "2023级", "AI1班", 3.95, "wangwu@school.edu", "13800000003", "2023-09-01"], [4, "2024004", "赵六", 20, "女", "数据科学", "2023级", "数据1班", 3.6, "zhaoliu@school.edu", "13800000004", "2023-09-01"], [5, "2024005", "钱七", 22, "男", "计算机科学与技术", "2022级", "计科2班", 3.45, "qianqi@school.edu", "13800000005", "2022-09-01"], [6, "2024006", "孙八", 19, "女", "软件工程", "2024级", "软工1班", 3.88, "sunba@school.edu", "13800000006", "2024-09-01"], [7, "2024007", "周九", 20, "男", "网络工程", "2023级", "网工1班", 3.2, "zhoujiu@school.edu", "13800000007", "2023-09-01"], [8, "2024008", "吴十", 21, "女", "人工智能", "2022级", "AI2班", 3.91, "wushi@school.edu", "13800000008", "2022-09-01"], [9, "2024009", "郑十一", 19, "男", "数据科学", "2024级", "数据2班", 3.55, "zhengshiyi@school.edu", "13800000009", "2024-09-01"], [10, "2024010", "王十二", 22, "女", "计算机科学与技术", "2022级", "计科3班", 3.78, "wangshier@school.edu", "13800000010", "2022-09-01"]]
# AI:以下是其他学生的信息（共10名学生，已包含张三）：
#
# 1. **李四**：19岁，女，软件工程专业，2024级，软工2班，绩点3.72
# 2. **王五**：21岁，男，人工智能专业，2023级，AI1班，绩点3.95
# 3. **赵六**：20岁，女，数据科学专业，2023级，数据1班，绩点3.60
# 4. **钱七**：22岁，男，计算机科学与技术专业，2022级，计科2班，绩点3.45
# 5. **孙八**：19岁，女，软件工程专业，2024级，软工1班，绩点3.88
# 6. **周九**：20岁，男，网络工程专业，2023级，网工1班，绩点3.20
# 7. **吴十**：21岁，女，人工智能专业，2022级，AI2班，绩点3.91
# 8. **郑十一**：19岁，男，数据科学专业，2024级，数据2班，绩点3.55
# 9. **王十二**：22岁，女，计算机科学与技术专业，2022级，计科3班，绩点3.78
#
# 如需按专业、年级、班级或绩点排序，或查询某位学生的详细信息，请告诉我。
# 你: