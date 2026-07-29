import json
from openai import OpenAI
from datetime import datetime


def get_time():
    return datetime.now()


# 函数到tool的映射
func_list = {
    "get_time": get_time
}

# 工具描述
tool_description = [{
    "type": "function",
    "function": {
        "name": "get_time",
        "description": "获取当前时间，不需要参数",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
}]

client = OpenAI(
    api_key="sk-96c0a475965841fd9b6b95276e5b68ba",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# history = []
StreamMode = False
ThinkingMode = False

if ThinkingMode:
    history = [{"role": "system",
                "content": "你是一个严肃的私人助理,你在回答我的问题前加一句：“主人你好！”,在回答问题时先在【思考】标签中写出你的推理过程， 然后在【答案】标签中给出最终答案"}]
else:
    history = [{"role": "system",
                "content": "你是一个严肃的私人助理,你在回答我的问题前加一句：“主人你好！”,在需要调用工具的场景你要根据tools描述调用我编写的工具 "}]

# 多轮对话循环
while True:
    text = input("你：")

    # 输入为空跳出本次循环
    if text.isspace():
        continue
    # 循环终止
    if text == "exit":
        break

    # 记忆
    history.append({"role": "user", "content": text})

    # 接下来进行StreamMode是否流式输出的判断
    # 流式输出
    # if StreamMode:
    #     response = client.chat.completions.create(
    #         model="qwen-plus",
    #         stream=True,
    #         messages=history,
    #         tools=tool_description
    #     )
    #     answer = ""
    #     for chunk in response:
    #         # print(chunk)
    #         delta = chunk.choices[0].delta.content
    #         answer += delta
    #         print(delta, end="", flush=True)
    #     print()
    #     history.append({"role": "assistant", "content": answer})

    # 非流式输出 先从非流式输出设计Function Call

    response = client.chat.completions.create(
            model="qwen-plus",
            stream=False,
            messages=history,
            temperature=0.8,
            tools = tool_description
        )

    curr_msg = response.choices[0].message
    history.append(curr_msg.model_dump())
    if curr_msg.tool_calls:
        #单个工具调用，提取工具
        tool_call = curr_msg.tool_calls[0]
        print("tool_call: " + tool_call.__str__())
        tool_name = tool_call.function.name
        print("模型调用的工具为：" + tool_name)

        args = json.loads(tool_call.function.arguments)
        print("args:" + args.__str__())
        func = func_list[tool_name]
        print("func:" + func.__str__())
        result = func(**args)
        print("result：" + result.__str__())

        tool_msg = {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        }
        history.append(tool_msg)

        final_responce = client.chat.completions.create(
            model = "qwen-plus",
            stream = False,
            messages = history,
            temperature = 0.8,
            tools = tool_description
        )

        answer = final_responce.choices[0].message.content
        print("AI:" + answer)
        history.append({"role": "assistant","content": answer})

    else:
        final_answer = curr_msg.content
        print("AI:", final_answer)
        history.append({"role": "assistant", "content": final_answer})

    # print("AI:", answer)

    # print(history)



# 你：hi
# AI: 主人你好！
# 你：现在几点了
# tool_call: ChatCompletionMessageFunctionToolCall(id='call_3cb1ae29535b433690f664', function=Function(arguments='{}', name='get_time'), type='function', index=0)
# 模型调用的工具为：get_time
# args:{}
# func:<function get_time at 0x0000023884F9DA80>
# result：2026-07-29 22:43:55.503069
# AI:现在是2026年7月29日，晚上10点43分55秒。
# 你：