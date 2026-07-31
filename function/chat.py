import dashscope


def init_client():
    api_key = "sk-96c0a475965841fd9b6b95276e5b68ba"
    dashscope.api_key = api_key


def create_messages(system_prompt=None):
    if system_prompt:
        return [{"role": "system", "content": system_prompt}]
    return []


def chat_loop(messages):
    from dashscope import Generation
    
    print("=" * 50)
    print("多轮对话已开始（输入 'quit' 退出）")
    print("=" * 50)
    
    while True:
        user_input = input("\n你: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ("quit", "exit", "q"):
            print("\n对话结束，再见！")
            break

        messages.append({"role": "user", "content": user_input})
        
        try:
            response = Generation.call(
                model="qwen-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # print(f"[调试] 状态码: {response.status_code}")
            # print(f"[调试] 原始响应: {response}")
            
            if response.status_code == 200:
                reply = response.output.text
                
                # 添加 AI 回复到历史
                messages.append({"role": "assistant", "content": reply})
                
                print(f"\nAI: {reply}")
            else:
                print(f"\n错误: {response.message}")
                
        except Exception as e:
            import traceback
            print(f"\n错误: {e}")
            traceback.print_exc()


def main():
    try:
        init_client()
        system_prompt = "你是一个专业、友善的AI助手，回答问题简洁明了。"
        messages = create_messages(system_prompt)
        chat_loop(messages)
        
    except ValueError as e:
        print(f"配置错误: {e}")
    except KeyboardInterrupt:
        print("对话中断")

if __name__ == "__main__":
    main()
