from openai import OpenAI
from datetime import datetime

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


# 你：hi
# 主人你好！
# 你：我爱吃苹果
# 主人你好！
# 【思考】用户表达了对苹果的喜爱，这是一个简单的陈述句，没有提出具体问题或需要执行的任务。因此，我只需友好回应，确认并适当延伸话题即可。
# 【答案】真棒！苹果既美味又健康，富含维生素和膳食纤维～你最喜欢哪种苹果呢？比如脆甜的富士、酸甜的嘎啦，还是红彤彤的蛇果？
# 你：我爱吃啥？
# 主人你好！
# 【思考】用户刚刚明确说过“我爱吃苹果”，现在问“我爱吃啥？”，可能是想确认、测试记忆，或带点俏皮的自我提问。作为助理，应准确复述其先前声明，并保持亲切自然的语气。
# 【答案】你刚才说：“我爱吃苹果”～🍎