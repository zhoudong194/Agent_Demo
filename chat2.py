from openai import OpenAI
from sympy import true

client = OpenAI(
    api_key="sk-96c0a475965841fd9b6b95276e5b68ba",
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
 )

# history = []
history = [{"role": "system", "content": "你是一个严肃的私人助理"}]

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

 response = client.chat.completions.create(
    model = "qwen-plus",
    messages = history,
    temperature = 0.8
 )

 answer = response.choices[0].message.content
 print("AI:", answer)

 history.append({"role": "assistant", "content": answer})

 print(history)