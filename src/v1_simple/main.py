from openai import OpenAI
import dotenv
import os

dotenv.load_dotenv()

def get_deepseek_response(prompt, temperature=None):
    # 1. 极简初始化：直接填入 DeepSeek 的配置
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )

    # 2. 发送一次性请求（建议用 try-except 包裹）
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content":"你是我的一个助手"},
                {"role": "user", "content":prompt},
            ],
            stream=False, #控制流式输出模式的开关
            temperature=temperature or 0 #控制模型“随机性”
        )
        return response
    
    except Exception as e:
        print(e)
        return None

def main():
    while True:
        print("\n================ 命令行版本 DeepSeek ================")
        print("                （输入序号表示选择对应功能）")
        print("             1. 一次普通问答")
        print("             2. 一次普通问答 + 模型完整对象打印")
        print("             3. 一次普通问答 + Usage 统计")
        print("             4. 一次“有温度“的问答（改变 temperature 参数）")
        print("             0. 退出")

        def tmp_ask(temp=None, cb=None):
            prompt = input("问：")
            response = get_deepseek_response(prompt, temp)
            if response:
                print("答：\n" + response.choices[0].message.content)
                if cb!=None:
                    cb(response)

        word = input()
        match word:
            case "0":
                break

            case "1":
                tmp_ask()
            
            case "2":
                def _cb(response):
                    print("模型完整对象打印：")
                    print(response.model_dump_json(indent=2))

                tmp_ask(None, _cb)

            case "3":
                def _cb(response):
                    usage = response.usage
                    print("Token 统计信息：")
                    print(f"输入：{usage.prompt_tokens}")
                    print(f"输出：{usage.completion_tokens}")
                    print(f"总计：{usage.total_tokens}")
                
                tmp_ask(None, _cb)
            
            case "4":
                temp = 2
                print(f"测试温度：{temp}")
                tmp_ask(temp)

            case _:
                print("输入有误！")
                continue
        

if __name__ == "__main__":
    main()