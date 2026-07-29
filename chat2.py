from modelscope.preprocessors.templates.tools_prompt import tools_prompt
from openai import OpenAI
from datetime import datetime

from pypinyin.runner import func_map


def get_time():
    return datetime.now()

#函数到tool的映射
func_list={
    "get_time":get_time
}

#工具描述
tool_description = [{
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前时间，不需要参数",
            "parameters": {
                "type":"object",
                "properties":{}
            }
        }
}]
client = OpenAI(
    api_key="sk-96c0a475965841fd9b6b95276e5b68ba",
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
 )

# history = []
StreamMode = True
ThinkingMode = True

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

 #接下来进行StreamMode是否流式输出的判断
 # 流式输出 
 if StreamMode:
    response = client.chat.completions.create(
        model = "qwen-plus",
        stream = True,
        messages = history,
        tools=tool_description
    )
    answer = ""
    for chunk in response:
        # print(chunk)
        delta = chunk.choices[0].delta.content
        answer += delta
        print(delta, end = "", flush = True)
    print()
    history.append({"role": "assistant", "content": answer})

 # 非流式输出
 else:
    response = client.chat.completions.create(
        model = "qwen-plus",
        stream = False,
        messages = history,
        temperature = 0.8,
        tools=tool_description
    )
    answer = response.choices[0].message.content
    print("AI:", answer)
 
 # print(history)