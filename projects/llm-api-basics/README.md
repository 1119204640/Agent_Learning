# LLM API 入门

从零调用大模型 API — 基于 DeepSeek + OpenAI SDK。

## 功能

交互式命令行程序，支持：
1. 普通问答
2. 完整模型响应对象打印（JSON）
3. Token 用量统计（含缓存命中）
4. Temperature 对比实验（0 vs 2）
5. JSON 模式强制输出（TODO）
6. Function Calling（TODO）

## 运行

```bash
uv sync
uv run python main.py
```

## .env 配置

复制 `.env.example` 为 `.env`，填入 DeepSeek API Key。
