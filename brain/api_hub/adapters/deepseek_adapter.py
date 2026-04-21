# deepseek_adapter.py
# ─────────────────────────────────────────────────────────────────────────────
# 模块职责：DeepSeek 模型适配器
# ─────────────────────────────────────────────────────────────────────────────
#
# 概述：
#   将 DeepSeek API 包装为系统内部统一的 BrainAdapter 接口。
#   DeepSeek 兼容 OpenAI 协议，因此本适配器主要负责：
#     - 配置 DeepSeek 专属的 Base URL 与默认模型名称
#     - 设置适合"商务/逻辑强推理"场景的默认参数
#     - 处理 DeepSeek 特有的响应字段（如 reasoning_content）
#
# 适用场景（对应 PRD 2.3 & 2.5）：
#   - 商务场景优先推荐使用 DeepSeek（强逻辑、行动项补全、架构分析）
#   - 默认模型：deepseek-chat / deepseek-reasoner（按场景切换）
#
# 配置项（来自 config/models.yaml）：
#   api_key    : 用户自持的 DeepSeek API Key（BYOK，不上报）
#   base_url   : https://api.deepseek.com/v1
#   model      : deepseek-chat
#   temperature: 0.7（商务场景建议降低至 0.3）
#   max_tokens : 512（Ghost Text 补全场景，控制响应长度）
#
# 继承关系：
#   DeepSeekAdapter(BaseAdapter)
#     └─ 实现 BaseAdapter 定义的统一接口
#
# 待实现方法：
#   __init__(config: AdapterConfig) -> None
#       初始化 OpenAI 兼容客户端，注入 DeepSeek base_url
#
#   complete(prompt: str, context: PromptContext) -> str
#       调用 chat/completions 接口，返回补全文本
#
#   stream_complete(prompt: str, context: PromptContext) -> AsyncIterator[str]
#       流式调用，支持逐 token 渲染幽灵文本（Ghost Text 实时刷新）
#
#   health_check() -> bool
#       检测 API Key 有效性与网络连通性
#
#   estimate_cost(prompt_tokens: int, completion_tokens: int) -> float
#       根据 DeepSeek 当前定价估算本次调用成本（用于 UI 成本面板展示）
#
# 依赖：
#   brain/api_hub/adapters/__init__.py  —— BaseAdapter 基类定义
#   config/models.yaml                  —— API Key 与模型参数读取
#
# 注意事项：
#   - API Key 必须从 config/secrets.yaml 或环境变量读取，禁止硬编码
#   - reasoning_content 字段（DeepSeek-R 系列）应单独存储，不混入 Ghost Text
#   - 网络超时需设置合理阈值（建议 5s），超时后降级到本地缓存建议
# ─────────────────────────────────────────────────────────────────────────────
