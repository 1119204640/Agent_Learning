# 从游戏开发自学转 AI Agent 工程师

> 每个阶段一个独立项目，学完一个再开下一个 · macOS + VS Code

## 学习路线

### 基础阶段：LLM + Web 框架

| # | 项目 | 状态 | 关键词 |
|---|------|------|--------|
| 1 | [LLM API 入门](https://github.com/1119204640/hello-llm-api) | 🚧 进行中 | DeepSeek, OpenAI SDK, Temperature, Token |
| 2 | [FastAPI 基础](https://github.com/1119204640/hello-fastapi) | ✅ 完成 | 路由, Pydantic 校验, Swagger 文档 |
| 3 | [Apple Notes 排版 Agent](https://github.com/1119204640/apple-notes-agent) | ✅ 完成 | FastAPI + LLM 实战, Docker 部署, Prompt 工程 |

### 进阶阶段：Agent 核心能力

| # | 项目 | 状态 | 关键词 |
|---|------|------|--------|
| 4 | Function Calling | ⬜ 待开始 | Tool Use, JSON Schema, 工具调用 |
| 5 | 异步 + 流式输出 | ⬜ 待开始 | asyncio, SSE, 打字机效果 |
| 6 | ReAct Agent 循环 | ⬜ 待开始 | Think→Act→Observe, 自主决策 |
| 7 | 多工具 Agent | ⬜ 待开始 | 工具编排, 错误恢复, 上下文管理 |
| 8 | RAG + 长期记忆 | ⬜ 待开始 | 向量检索, Embedding, 记忆系统 |

---

## 环境：Python + uv

macOS 下 Python 包管理容易陷入路径地狱（系统 Python / pyenv / venv 混在一起），用 `uv` 解决：

```bash
brew install uv
uv init my_project        # 项目初始化
uv add python-dotenv      # 添加依赖
uv add openai
uv run python main.py     # 直接运行，环境自动隔离
```

### API Key 安全惯例

- 用 `python-dotenv` 从 `.env` 加载敏感信息
- `.env` 加入 `.gitignore`，`.env.example` 作为模板提交

---

## 项目 1：LLM API 入门

**代码：** [hello-llm-api](https://github.com/1119204640/hello-llm-api)

### 学到了什么

**API 调用基础**
- DeepSeek 兼容 OpenAI SDK，改 `base_url` 即可切换服务商
- 网络请求必须包 `try...except`，API 可能超时或返回异常

**响应解析**

| 字段 | 含义 |
|------|------|
| `response.choices[0].message.content` | AI 回复的文本 |
| `response.usage.total_tokens` | 总 Token 消耗 |
| `response.usage.prompt_cache_hit_tokens` | 命中缓存的 Token 数（DeepSeek 特色，省钱） |
| `response.choices[0].finish_reason` | `stop` 正常结束 / `length` 超长截断 |

调试时用 `response.model_dump_json(indent=2)` 比 `print(response)` 清晰得多。

**Temperature — 控制随机性**

```python
response = client.chat.completions.create(..., temperature=t)
```

- `t = 0`：贪婪搜索，每次选概率最高的词。结果稳定，适合代码、事实问答
- `t = 2`：可能选低概率词，结果每次不同。适合写诗、脑暴，但容易产生幻觉

同一个 prompt「简短描述一只小猫」：`t=0` 返回正常描述，`t=2` 返回乱码。

**LLM 原理要点**
- 本质是 Next Token Prediction：给定上文，预测下一个字（Token）的概率分布
- 训练三部曲：预训练（海量语料）→ 指令微调（学会对话格式）→ RLHF（学会好坏）
- 幻觉不可避免，对关键事实必须人工复核

**Prompt 技巧**

| 技巧 | 做法 |
|------|------|
| Zero-shot | 直接下指令，不给例子 |
| Few-shot | 给 2-3 个示范案例，格式即约定 |
| Chain of Thought | 让模型先写出推导过程，再给答案 |

**JSON 模式 — Agent 的基础**

Agent 需要可解析的确定输出（调哪个函数、传什么参数），不能依赖自然语言。两种方式：
- **软约束**：System Prompt 里要求「只输出 JSON」，但模型偶尔会在前面加废话
- **强约束**：`response_format={'type': 'json_object'}`，保证输出合法 JSON

```python
response = client.chat.completions.create(
    ..., response_format={'type': 'json_object'}
)
```

---

## 项目 2：FastAPI 基础

**代码：** [hello-fastapi](https://github.com/1119204640/hello-fastapi)

### 学到了什么

Agent 最终要以 HTTP 服务的形式暴露给用户，FastAPI 是目前最流行的 Python 异步 Web 框架。

**路由与请求方法**
- `@app.get()` / `@app.post()` 装饰器定义端点
- 路径参数 `/{name}` 和查询参数 `?limit=10&min_mood=50` 的区别
- FastAPI 自带 Swagger UI（`/docs`）和 ReDoc（`/redoc`），无需额外配置

**Pydantic 请求校验**
```python
class Content(BaseModel):
    text: str = Field(..., min_length=5)
```
- FastAPI 自动解析 JSON 请求体 → Python 对象
- 校验失败自动返回 422，不执行业务逻辑
- `json_schema_extra` 提供示例值，直接显示在 Swagger 里

**三种接口模式演示**

| 接口 | 类型 | 演示要点 |
|------|------|----------|
| `GET /` | 无参数 | 最简单的欢迎页 |
| `GET /hello/{name}` | 路径参数 | URL 嵌入动态值 |
| `GET /history?limit=&min_mood=` | 查询参数 | `?key=value` 可选参数 |
| `POST /analyze` | 请求体 | JSON body + Pydantic 校验 |

---

## 项目 3：Apple Notes 排版 Agent

**代码：** [apple-notes-agent](https://github.com/1119204640/apple-notes-agent)

### 学到了什么

这是第一个「LLM + Web 框架」组合的实战项目，已部署到云服务器。

**系统架构**

```
iPhone Shortcut → POST /api/v1/format → FastAPI → DeepSeek-V3 → Markdown  → Apple Notes
                                         (Pydantic)   (AsyncOpenAI)   (纯文本)
```

**Prompt 工程设计**
- 18 行 system prompt 精确控制输出格式
- 强制规则：纯 Markdown、不输出代码块包装、不输出"好的，为您整理如下"
- `temperature=0.3` 保证格式稳定
- 保底后处理：正则替换清理异常换行

**项目结构分拆**
```
apple-notes-agent/
├── main.py              # FastAPI 入口，单端点
├── core/config.py       # pydantic-settings 读取 .env
├── models/schemas.py    # 请求体模型
└── services/llm_service.py  # LLM 调用 + system prompt
```
三个职责分离：配置 / 数据契约 / AI 逻辑 — 这是 Agent 项目的标准骨架。

**Docker 部署**
- 多阶段构建（uv 官方镜像 → python:3.11-slim）
- 内存限制 256MB（保护同一台服务器的 Minecraft）
- `deploy.sh` 一键：构建 → 打包 → scp 上传 → 远程启动 → 健康检查

---

## 踩坑记录

- `stream=True` 后 response 的取法完全不同，不能用 `.choices[0].message.content`
- `model_dump_json` 是 Pydantic 模型的方法，不是 dict 的 — 只对 response 对象有效
