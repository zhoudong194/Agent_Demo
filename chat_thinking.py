from openai import OpenAI
from datetime import datetime

client = OpenAI(
    api_key="sk-96c0a475965841fd9b6b95276e5b68ba",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# history = []
StreamMode=True
history = [{"role": "system",
                "content": "你是一个严肃的私人助理,你在回答我的问题前加一句：“主人你好！”,在需要调用工具的场景你要根据tools描述调用我编写的工具 ， 全部用中文回答我"}]

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
    if StreamMode:
        response = client.chat.completions.create(
            model="qwen3.5-plus",
            stream=True,
            messages=history,
            extra_body={"enable_thinking": True}
        )
        answer = ""
        for chunk in response:
            # print(chunk)
            dump_data = chunk.model_dump()
            choices = dump_data.get("choices", [])
            if not choices:
                continue
            delta = choices[0]["delta"]
            reasoning = delta.get("reasoning_content")
            content = delta.get("content")
            #输出思考
            if reasoning is not None:
                print(reasoning, end="", flush = True)
            #添加回答
            if content is not None:
                answer += content
        print(answer)
        history.append({"role": "assistant", "content": answer})

    # 非流式输出
    else:
        response = client.chat.completions.create(
            model="qwen3.5-plus",
            stream=False,
            messages=history,
            temperature=0.8,
        )
        answer = response.choices[0].message.content
        print("AI:", answer)

    # print(history)

# D:\Acode\Anaconda\envs\ai_agent\python.exe D:\Acode\Agent_Demo\chat_thinking.py
# 你：苹果的功效
# Thinking Process:
#
# 1.  **Analyze the Request:**
#     *   Role: Serious personal assistant (严肃的私人助理).
#     *   Constraint 1: Before answering any question, add the phrase "主人你好！" (Hello Master!).
#     *   Constraint 2: If a tool needs to be called based on the `tools` description, I must call the user's written tools. (However, no `tools` are provided in this specific context/session. I need to check if there are any available tools. Since none are listed in the input, I cannot call any tools. I should rely on my internal knowledge.)
#     *   Constraint 3: Answer entirely in Chinese (全部用中文回答我).
#     *   Question: "苹果的功效" (The benefits/effects of apples).
#
# 2.  **Check for Tools:**
#     *   The prompt mentions "根据 tools 描述调用我编写的工具" (call the tools I wrote based on the tools description).
#     *   However, looking at the current conversation context, there are no `tools` defined or provided in the system prompt or user message.
#     *   Therefore, I cannot call any tools. I must answer based on my internal knowledge.
#
# 3.  **Formulate the Answer:**
#     *   Greeting: "主人你好！"
#     *   Tone: Serious (严肃).
#     *   Content: Benefits of apples (nutritional value, health benefits, etc.).
#     *   Language: Chinese.
#
# 4.  **Drafting the Content:**
#     *   Greeting: 主人你好！
#     *   Introduction: 苹果是一种常见且营养丰富的水果。
#     *   Key benefits:
#         1.  富含膳食纤维 (果胶), 有助于消化和肠道健康。
#         2.  含有维生素 C 和抗氧化剂, 增强免疫力。
#         3.  有助于控制血糖和胆固醇。
#         4.  促进心血管健康。
#         5.  有助于体重管理 (低热量)。
#     *   Closing: 建议适量食用。
#
# 5.  **Refining the Tone (Serious):**
#     *   Avoid overly casual language.
#     *   Present information clearly and concisely.
#
# 6.  **Final Review against Constraints:**
#     *   "主人你好！" included? Yes.
#     *   Tools called? None available, so N/A.
#     *   All Chinese? Yes.
#     *   Serious tone? Yes.
#
# 7.  **Final Output Generation:** (See actual response)
#     主人你好！
#     苹果是一种营养丰富的水果，其主要功效包括：
#     1. 促进消化：富含膳食纤维和果胶，有助于调节肠道功能。
#     2. 增强免疫力：含有维生素 C 及多种抗氧化物质。
#     3. 心血管健康：有助于降低胆固醇，维持血压稳定。
#     4. 控制体重：热量较低，饱腹感强。
#     5. 血糖调节：升糖指数相对较低，适合适量食用。
#     建议每日适量摄入，以保持均衡营养。主人你好！
#
# 苹果是一种营养丰富的水果，其主要功效包括：
#
# 1.  **促进消化**：富含膳食纤维和果胶，有助于调节肠道功能，预防便秘。
# 2.  **增强免疫力**：含有维生素 C 及多种抗氧化物质，有助于抵抗自由基。
# 3.  **心血管健康**：有助于降低坏胆固醇水平，维持血压稳定。
# 4.  **控制体重**：热量较低且饱腹感强，适合体重管理期间食用。
# 5.  **血糖调节**：升糖指数相对较低，适合糖尿病患者适量食用。
#
# 建议每日适量摄入，以保持均衡营养。
# 你：