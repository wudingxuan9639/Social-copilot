# API 接入指南 (API Integration Guide)

> 对应 PRD 2.3 — 极致灵活的 API 接入 (Flexible Hub / BYOK)

本文档面向开发者，说明如何在 Social Copilot 中接入、配置和扩展外部 AI 模型 API。

---

## 目录

1. [核心设计原则](#1-核心设计原则)
2. [支持的服务商与默认配置](#2-支持的服务商与默认配置)
3. [配置文件结构](#3-配置文件结构)
4. [快速接入示例](#4-快速接入示例)
5. [自定义 Adapter 开发指南](#5-自定义-adapter-开发指南)
6. [场景路由规则](#6-场景路由规则)
7. [安全与密钥管理](#7-安全与密钥管理)
8. [常见问题排查](#8-常见问题排查)

---

## 1. 核心设计原则

### BYOK（Bring Your Own Key）
Social Copilot **不内置任何 AI 能力**，也不托管用户的 API Key。
所有 AI 能力均来自用户自行申请的第三方服务。软件只负责将本地上下文
（用户人设 + 联系人标签 + 对话片段）组装为 Prompt，通过用户提供的 Key 发起调用。

### 协议兼容层
系统统一基于 **OpenAI Chat Completions 协议**进行调度。
各服务商适配器（Adapter）负责抹平接口差异，上层路由器（Router）无需关心具体服务商。

```
用户的 API Key（存于本地 config/models.yaml）
        │
        ▼
brain/api_hub/config.py  — 加载配置
        │
        ▼
brain/api_hub/router.py  — 按场景标签选择 Adapter
        │
        ├─> DeepSeekAdapter   (商务场景)
        ├─> DoubaoAdapter     (亲密场景)
        └─> OpenAIAdapter     (默认 / 自定义)
```

### 无状态原则
`brain/` 层是无状态的：API Key 仅在内存中短暂存在，不写入日志，不持久化到数据库。

---

## 2. 支持的服务商与默认配置

| 服务商 | 推荐场景 | 默认模型 | Base URL |
|--------|----------|----------|----------|
| **DeepSeek** | 商务场景（强逻辑） | `deepseek-chat` | `https://api.deepseek.com/v1` |
| **豆包 (Doubao)** | 亲密场景（拟人化） | `<endpoint_id>` | `https://ark.cn-beijing.volces.com/api/v3` |
| **通义千问 (Qwen)** | 通用 | `qwen-plus` | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| **OpenAI** | 通用 / 默认 | `gpt-4o-mini` | `https://api.openai.com/v1` |
| **自定义 (Custom)** | 任意 | 用户填写 | 用户填写 |

> **注意**：所有服务商均需兼容 OpenAI Chat Completions 协议（`/chat/completions` 端点）。
> 如服务商 API 协议不兼容，需额外开发 Adapter 进行转换（见[第 5 节](#5-自定义-adapter-开发指南)）。

---

## 3. 配置文件结构

API 配置存储在 `config/models.yaml`。敏感字段（API Key）应通过环境变量引用。

### 完整配置示例

```yaml
# config/models.yaml
# ⚠️  请勿将此文件提交到 Git（已加入 .gitignore）

version: "1.0"

# 默认模型（无法识别场景时使用）
default:
  provider: openai
  base_url: "https://api.openai.com/v1"
  api_key: "${OPENAI_API_KEY}"        # 从环境变量读取
  model: "gpt-4o-mini"
  temperature: 0.7
  max_tokens: 512
  timeout_seconds: 10
  enabled: true

# 商务场景专用模型
business:
  provider: deepseek
  base_url: "https://api.deepseek.com/v1"
  api_key: "${DEEPSEEK_API_KEY}"
  model: "deepseek-chat"
  temperature: 0.3                    # 商务场景降低随机性，输出更严谨
  max_tokens: 512
  timeout_seconds: 10
  enabled: true

# 亲密场景专用模型
intimate:
  provider: doubao
  base_url: "https://ark.cn-beijing.volces.com/api/v3"
  api_key: "${DOUBAO_API_KEY}"
  model: "ep-xxxxxxxx-xxxx"           # 替换为你的豆包 Endpoint ID
  temperature: 0.85                   # 亲密场景提高随机性，表达更自然
  max_tokens: 256
  timeout_seconds: 10
  enabled: true

# 兜底模型（当首选模型调用失败时使用）
fallback:
  provider: openai
  base_url: "https://api.openai.com/v1"
  api_key: "${OPENAI_API_KEY}"
  model: "gpt-3.5-turbo"
  temperature: 0.7
  max_tokens: 256
  timeout_seconds: 8
  enabled: true

# 全局参数
global:
  retry_max: 2                        # 请求失败后最大重试次数
  retry_backoff_seconds: 1.5          # 重试指数退避基数
  stream: true                        # 是否启用流式输出（Ghost Text 实时渲染）
  log_token_usage: true               # 是否在控制台输出 Token 用量统计
  cost_alert_usd: 0.10                # 单次对话超过此费用时弹出提示
```

### 环境变量配置（推荐方式）

在项目根目录创建 `.env` 文件（已加入 `.gitignore`，不会被提交）：

```bash
# .env（请勿提交到版本控制）

OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DOUBAO_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 4. 快速接入示例

### 场景一：仅使用 DeepSeek（全场景统一）

适合只想接一个 API、不区分场景的简单配置：

```yaml
# config/models.yaml（最简版）

default:
  provider: deepseek
  base_url: "https://api.deepseek.com/v1"
  api_key: "${DEEPSEEK_API_KEY}"
  model: "deepseek-chat"
  temperature: 0.7
  max_tokens: 512
  enabled: true

business:
  <<: *default         # YAML 锚点复用 default 配置

intimate:
  <<: *default
  temperature: 0.85    # 亲密场景单独调高温度

fallback:
  <<: *default
```

### 场景二：DeepSeek（商务）+ 豆包（亲密）双模型配置

```yaml
business:
  provider: deepseek
  base_url: "https://api.deepseek.com/v1"
  api_key: "${DEEPSEEK_API_KEY}"
  model: "deepseek-chat"
  temperature: 0.3

intimate:
  provider: doubao
  base_url: "https://ark.cn-beijing.volces.com/api/v3"
  api_key: "${DOUBAO_API_KEY}"
  model: "ep-20240716-xxxxxxxx"
  temperature: 0.85
```

### 场景三：接入本地部署模型（Ollama）

只要模型服务暴露兼容 OpenAI 协议的接口，即可直接接入：

```yaml
default:
  provider: custom
  base_url: "http://localhost:11434/v1"   # Ollama 本地服务
  api_key: "ollama"                        # Ollama 不需要真实 Key，填占位符
  model: "qwen2.5:7b"
  temperature: 0.7
  max_tokens: 512
```

---

## 5. 自定义 Adapter 开发指南

如需接入协议不兼容 OpenAI 的服务商，按以下步骤新增 Adapter：

### 步骤一：在 `brain/api_hub/adapters/` 新建适配器文件

```
brain/api_hub/adapters/
└── my_custom_adapter.py   ← 新建此文件
```

### 步骤二：继承 `BaseAdapter` 并实现接口

```python
# brain/api_hub/adapters/my_custom_adapter.py

from brain.api_hub.adapters import BaseAdapter, AdapterConfig, GenerationResult

class MyCustomAdapter(BaseAdapter):
    """
    自定义模型适配器骨架（此处不写实现代码，仅说明接口契约）
    """

    def __init__(self, config: AdapterConfig) -> None:
        """
        初始化适配器
        - 接收配置对象（api_key, base_url, model, temperature, max_tokens）
        - 初始化 HTTP 客户端
        """
        ...

    async def complete(self, prompt: str, system: str) -> GenerationResult:
        """
        非流式补全接口
        - 发起单次请求，等待完整响应后返回
        - 返回 GenerationResult（含 text, token_usage, latency_ms）
        """
        ...

    async def stream_complete(self, prompt: str, system: str):
        """
        流式补全接口（AsyncGenerator）
        - 逐 token 产出文本片段
        - 用于 Ghost Text 实时渲染
        """
        ...

    async def health_check(self) -> bool:
        """
        健康检测
        - 发送轻量请求验证 API Key 有效性与服务可达性
        - 用于「测试连接」按钮
        """
        ...
```

### 步骤三：在 `adapters/__init__.py` 注册

```python
# brain/api_hub/adapters/__init__.py（在此处注册新适配器）

ADAPTER_REGISTRY = {
    "openai":   OpenAIAdapter,
    "deepseek": DeepSeekAdapter,
    "doubao":   DoubaoAdapter,
    "my_custom": MyCustomAdapter,    # ← 新增注册
}
```

### 步骤四：在 `config/models.yaml` 中使用

```yaml
default:
  provider: my_custom                  # ← 对应 ADAPTER_REGISTRY 的 key
  base_url: "https://your-api.com/v1"
  api_key: "${MY_CUSTOM_API_KEY}"
  model: "your-model-name"
```

---

## 6. 场景路由规则

Router 根据 `ContactTier`（联系人等级）自动选择对应模型配置：

```
ContactTier.BUSINESS  →  config["business"]  模型
ContactTier.INTIMATE  →  config["intimate"]  模型
ContactTier.SOCIAL    →  config["default"]   模型
ContactTier.UNKNOWN   →  config["default"]   模型

任何模型调用失败      →  config["fallback"]  模型（降级）
```

### 手动覆盖路由（高级用法）

用户可在设置面板中手动为某个联系人指定模型，优先级高于自动路由：

```yaml
# config/contact_overrides.yaml（由 UI 设置面板生成）

contact_overrides:
  - contact_id: "wxid_xxxxxxxxxx"
    display_name: "张总"
    force_scenario: "business"        # 强制使用商务场景配置
    force_model: null                 # null 表示使用场景默认模型

  - contact_id: "wxid_yyyyyyyyyy"
    display_name: "老婆"
    force_scenario: "intimate"
    force_model: "doubao"             # 进一步指定具体模型（覆盖场景默认）
```

---

## 7. 安全与密钥管理

### 密钥存储规则

| 存储位置 | 是否安全 | 说明 |
|----------|----------|------|
| 环境变量 `.env` | ✅ 推荐 | 不提交 Git，本机生效 |
| `config/models.yaml` 明文 | ⚠️ 可接受 | 已在 `.gitignore` 中，但明文留存于磁盘 |
| `config/secrets.yaml` | ✅ 推荐 | 独立密钥文件，单独 `.gitignore` 条目 |
| 代码中硬编码 | ❌ 禁止 | 绝对禁止，会被提交到 Git |
| 应用日志 / 控制台输出 | ❌ 禁止 | Key 字段严禁写入任何日志 |

### 密钥引用语法

在 `models.yaml` 中使用 `${ENV_VAR_NAME}` 语法引用环境变量，
`config.py` 在加载配置时会自动展开：

```yaml
api_key: "${DEEPSEEK_API_KEY}"   # 优先从环境变量读取
```

若环境变量未设置，配置加载器将抛出 `ConfigurationError` 并提示用户补充。

### 运行时密钥生命周期

```
models.yaml / .env
      │
      ▼ (应用启动时一次性读取)
config.py → ModelConfig.api_key: SecretStr
      │
      ▼ (每次 API 调用时传入 HTTP Header)
Adapter.complete(prompt, system)
      │
      ▼ (响应返回后)
SecretStr 在 GC 时释放，从不写入磁盘或日志
```

---

## 8. 常见问题排查

### Q1：按下 Tab 后没有触发 Ghost Text，AI 没有响应

**检查步骤：**
1. 确认 `config/models.yaml` 中对应场景的 `enabled: true`
2. 点击设置面板中的「测试连接」按钮，检查 API Key 有效性
3. 查看应用控制台，是否有 `AuthenticationError` 或 `ConnectionTimeoutError`

---

### Q2：DeepSeek 报错 `AuthenticationError: Invalid API Key`

**可能原因：**
- `.env` 中 `DEEPSEEK_API_KEY` 未设置或拼写错误
- `models.yaml` 中 `api_key` 字段写了字面量而非环境变量引用

**解决方式：**
```bash
# 验证环境变量是否正确加载
echo $DEEPSEEK_API_KEY

# 或直接在 .env 中写入（注意不要有多余空格）
DEEPSEEK_API_KEY=sk-your-actual-key-here
```

---

### Q3：豆包（Doubao）报错 `model not found`

**可能原因：**
- 豆包需要使用「推理接入点 ID」（`ep-xxxxxxxx-xxxx` 格式）作为模型名称，
  而不是通用模型名

**解决方式：**
1. 登录[火山方舟控制台](https://console.volcengine.com/ark)
2. 在「推理接入点」页面找到你创建的接入点 ID
3. 将该 ID 填入 `config/models.yaml` 的 `intimate.model` 字段：
   ```yaml
   intimate:
     model: "ep-20240716-xxxxxxxx"   # 替换为你的真实接入点 ID
   ```

---

### Q4：调用延迟过高，Ghost Text 响应太慢

**优化建议：**
- 开启流式输出（`global.stream: true`），让 Ghost Text 逐字渲染，减少感知延迟
- 降低 `max_tokens`（Ghost Text 补全场景建议 128~256，无需生成长文本）
- 将 `timeout_seconds` 调整为合理值（建议 5~8 秒）
- 商务场景尝试使用 `deepseek-chat`（国内节点，对国内用户延迟更低）

---

### Q5：如何在不重启应用的情况下热更新 API 配置？

在 UI 设置面板修改并保存配置后，系统会自动调用 `brain/api_hub/config.py` 中的
`reload_config()` 方法，Router 将在下次请求时使用新配置。
无需重启应用。

---

## 附录：各服务商 API Key 申请地址

| 服务商 | 申请地址 | 备注 |
|--------|----------|------|
| DeepSeek | https://platform.deepseek.com | 注册后在「API Keys」页面创建 |
| 豆包 / 火山方舟 | https://console.volcengine.com/ark | 需先创建「推理接入点」获取 Endpoint ID |
| 通义千问 | https://dashscope.aliyuncs.com | 阿里云账号，开通 DashScope 服务 |
| OpenAI | https://platform.openai.com | 国内访问可能需要代理 |

---

*文档版本：v1.0 | 对应 brain/api_hub/ 模块 | 更新时间：见 Git 提交记录*