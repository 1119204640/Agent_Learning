from openai import OpenAI
import dotenv
import os

dotenv.load_dotenv()

def main():
    # 1. 极简初始化：直接填入 DeepSeek 的配置
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )

    systemContent = "你是一个幽默的助手。"
    userContent = "用一句话证明你是一个AI。"

    print("⏳ 正在呼叫 DeepSeek...\n")

    print("角色设定："+ systemContent)
    print("发问内容：" + userContent)

    # 2. 发送一次性请求
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": systemContent},
            {"role": "user", "content": userContent}
        ]
    )

    # 3. 暴力打印结果
    print("\n🤖 回复：")
    print(response.choices[0].message.content + "\n")

if __name__ == "__main__":
    main()