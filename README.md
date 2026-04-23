# 从游戏开发自学转 Agent 工程师

*环境：macOS 26、VS code*

## 🛠️ 项目进度

### 子项目1：大模型 API 调用
- [x] 简单接入 DeepSeek API
- [x] 实现模型完整对象打印与 Usage 统计
- [x] 完成 Temperature (0 vs 1.3) 对比
- [ ] 增加 `client.py`，优化封装逻辑
- [ ] 重构为异步调用
- [ ] 实现流式打字机效果
- [ ] 增加上下文支持，管理记忆
- [ ] 实现 GUI 界面
- [ ] **终极目标：实现一个 markdown 转小红书图文的 app**

## Day 1

### Python 环境部署和优化

#### Python 安装
我本来已经安装好了，安装也很简单，这里不展开。也可等后面 uv 工具安装好之后再来安装 Python

#### macOS 下 Python 包管理极其混乱问题
- 路径地狱：电脑里同时存在系统 Python、pyenv 版本和 venv 环境。明明激活了环境，但 which pip 偶尔还是会指向别处，导致“库装在 A 处，程序去 B 处找”，引发 ModuleNotFoundError。

- 证书高墙 (SSL Error)： Mac + pyenv 环境极其“死板”，不带根证书，导致 Python 无法访问 HTTPS 网站。安装库时频繁被 CERTIFICATE_VERIFY_FAILED 拦截。

- 繁琐的仪式感：每次开新项目都要经历 mkdir -> venv -> source -> pip install -> pip install certifi 等一系列“规定动作”，不仅累，还容易忘。

#### 安装 uv 包与环境管理工具可以解决上述问题
- 安装 uv  
👉 `brew install uv`  
  
- 使用 uv 选一个你想存放项目的位置新建项目，并进行项目初始化，会自动帮你创建必须的工程文件  
👉 `uv init my_project`  
  
  - <u>后续全部直接用 uv 工具下载第三方库，详见[ uv 菜鸟教程 ](https://www.runoob.com/python3/uv-tutorial.html)</u>

- 安装 python-dotenv 库  
👉 `uv add python-dotenv`  
  - 用作管理环境变量，避免大模型的 api_key 被泄露  
  - 创建一个 .env 文件，声明一个环境变量（命名随意）  
  - 防止这个文件被 commit，要去 .gitignore 文件中确认是否忽略了这个后缀

- 安装 openai 库  
👉 `uv add openai`  
  - 用作调用 DeepSeek 的 API（在此之前，先去 DeepSeek 用一块钱购买 Tokens），虽然我们用的是 openai 库，但通过修改 base_url，我们可以给任何兼容 OpenAI 格式的服务发请求

### **API 调用**
   #### 来 `main.py` 写第一个最简单的版本：接入 DeepSeek API
   ```python
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
   ```

- 输出如下：  
```
  ⏳ 正在呼叫 DeepSeek...

  角色设定：你是一个幽默的助手。  
  发问内容：用一句话证明你是一个AI。

  🤖 回复：
  “我连‘饿’是什么感觉都不知道，毕竟我的电源线可比外卖快多了。”
```
      
## Day 2
### 模型完整对象打印与 Usage 统计
#### 核心 API
```python
# 获取回复内容
content = response.choices[0].message.content

# 获取总消耗 Token
total_usage = response.usage.total_tokens

# 获取命中的缓存 Token (DeepSeek 特色省钱点)
cache_hit = response.usage.prompt_cache_hit_tokens

# 当你执行 print(response) 时，你会看到一个类似 ChatCompletion(id='...', ...) 的对象。这是因为 openai 库为了方便开发者，把原始 JSON 封装成了 Python 对象。
# 使用 model_dump_json() 可以看到类似网页端的 JSON 源码
# 传入 indent=2 参数可以让 JSON 按照关键字换行和以2个字符作为缩进
print(response.model_dump_json(indent=2))
```

#### DeepSeek API 响应参数解析表

| 字段名 | 类型 | 含义说明 | 开发者关注度 |
| :--- | :--- | :--- | :--- |
| **`id`** | String | 此次对话的唯一标识符 | 🌕🌑🌑 |
| **`choices`** | List | 回答列表（通常包含一个对象） | 🌕🌕🌕 |
| └ **`message.content`** | String | **AI 回答的具体文字内容** | 🌕🌕🌕 |
| └ **`finish_reason`** | String | 停止原因（`stop` 为正常结束，`length` 为长度溢出） | 🌕🌕🌑 |
| **`usage`** | Object | 资源消耗统计（账单详情） | 🌕🌕🌕 |
| └ **`prompt_tokens`** | Int | 用户输入的 Token 数量 | 🌕🌕🌑 |
| └ **`completion_tokens`** | Int | AI 输出的 Token 数量 | 🌕🌕🌑 |
| └ **`total_tokens`** | Int | **总共消耗的 Token 数量** | 🌕🌕🌕 |
| └ **`prompt_cache_hit_tokens`** | Int | **命中上下文缓存的 Token 数 (省钱项)** | 🌕🌕🌕 |
| └ **`prompt_cache_miss_tokens`** | Int | 未命中缓存、需要重新计算的 Token 数 | 🌕🌕🌑 |
| **`created`** | Timestamp | 回应生成的 Unix 时间戳 | 🌕🌑🌑 |
| **`model`** | String | 使用的模型名称 (如 `deepseek-chat`) | 🌕🌑🌑 |
| **`system_fingerprint`** | String | 系统指纹 (模型服务器集群的版本标识) | 🌕🌑🌑 |

---

#### 细节注意
- 要给网络请求加 `try...except` “保护壳”
- Python 的函数回调方式跟 Lua 不太一样
- 在 create response 的时候，要注意 stream 这个参数的设置，用来控制流式输出模式的开关（详见下文的例子）

### Temperature (0 vs 2) 对比
- temperature 是控制模型“随机性”的开关
  - 温度 = 0 (严谨模式)：
    - 原理：模型每次都只选那个概率最大的词（贪婪搜索）。
    - 表现：回答非常稳定。如果你运行 10 次，结果几乎一模一样。适合写代码、算算术、事实问答。
  - 温度 = 2 (放飞模式)：
    - 原理：模型会更有可能选择那些概率较低的词。
    - 表现：回答极具文学性、意想不到甚至可能“胡言乱语”。每次运行结果都会变。适合写诗、起名、脑暴。

  ```python
  response = client.chat.completions.create(
              model="deepseek-chat",
              messages=[
                  {"role": "system", "content":"你是我的一个助手"},
                  {"role": "user", "content":prompt},
              ],
              temperature=temperature or 0 #控制模型“随机性”
          )
  ```

  - 同样是“简短描述一只小猫“，输出效果对比如下：
    - temperature = 0：“毛茸茸的小团子，琥珀色的眼睛亮晶晶的，尾巴轻轻摇晃，偶尔发出软糯的“喵”声。“
    - temperature = 2 时出现了幻觉：“一球洁白秋纺垂地瘫卧开漾尖角小羽绒把阳锁在外蹲时太阳恰不耀肉膜托出明悉朝蜇缩动的耳耳暖昧没滤过日光“