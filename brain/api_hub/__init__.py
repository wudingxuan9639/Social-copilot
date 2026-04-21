# brain/api_hub — 灵活 API 接入层 (Flexible Hub / BYOK)
#
# 对应 PRD 2.3 — 极致灵活的 API 接入
#
# 职责：
#   作为软件与外部 AI 模型之间的统一调度中枢。
#   本层不内置任何 AI 能力，仅负责将来自 brain/scenario 的
#   Prompt 请求，路由至用户自配置的外部模型 API 并返回结果。
#
# 核心设计原则：
#   - BYOK (Bring Your Own Key)：用户持有 API Key，软件不存储、不上报
#   - 协议兼容：统一适配 OpenAI Chat Completions 协议，各模型通过 Adapter 抹平差异
#   - 场景路由：根据联系人标签（business / intimate）自动选择对应模型配置
#   - 成本可控：Token 用量计数、超限熔断，避免意外超额消费
#
# 子模块：
#   router.py          — API 路由调度器，根据场景标签分发请求至目标 Adapter
#   config.py          — 模型配置管理（读取 config/models.yaml，不持有明文 Key）
#   adapters/          — 各厂商模型适配器目录
#     openai_adapter.py    — 标准 OpenAI / 任何兼容协议的通用适配器
#     deepseek_adapter.py  — DeepSeek 专用适配器（商务场景推荐）
#     doubao_adapter.py    — 豆包专用适配器（亲密场景推荐）
#
# 数据流：
#   ScenarioDetector 输出的 PromptPackage
#       └─> Router.dispatch(prompt_package)
#               └─> Adapter.call(payload) → stream / text
#                       └─> GhostText 渲染层
