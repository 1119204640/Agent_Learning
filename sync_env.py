import os

def sync_env():
    if not os.path.exists('.env'):
        print("未找到 .env 文件")
        return

    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    example_lines = []
    for line in lines:
        # 处理注释或空行
        if line.startswith('#') or not line.strip():
            example_lines.append(line)
        # 处理 键=值
        elif '=' in line:
            key = line.split('=')[0]
            example_lines.append(f"{key}=your_{key.lower()}_here\n")

    with open('.env.example', 'w', encoding='utf-8') as f:
        f.writelines(example_lines)
    
    print("✅ .env.example 已根据 .env 自动更新！")

if __name__ == "__main__":
    sync_env()