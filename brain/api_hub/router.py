# brain/api_hub/router.py
# =============================================================================
# 模块职责：多模型 API 路由调度器 (API Router)
# 对应 PRD 2.3 — 极致灵活的 API 接入 (Flexible Hub)
# =============================================================================
#
# 核心职责：
#   1. 根据联系人标签（ContactTier）自动选择最合适的模型配置
#   2. 将 Prompt + 上下文 分发给对应的模型适配器（Adapter）
#   3. 统一处理请求超时、重试、错误回退逻辑
#   4. 支持用户在 config/models.yaml 中自由配置模型路由规则
#
# 路由策略示例（对应 PRD 描述）：
#   ┌─────────────────────┬──────────────────────────────────────┐
#   │  ContactTier        │  默认模型建议                         │
#   ├─────────────────────┼──────────────────────────────────────┤
#   │  BUSINESS           │  DeepSeek（强逻辑、严谨）             │
#   │  INTIMATE           │  豆包（拟人化、情感表达）              │
#   │  SOCIAL / UNKNOWN   │  用户配置的默认模型                    │
#   └─────────────────────┴──────────────────────────────────────┘
#
# 数据流：
#   brain/scenario/detector.py (场景标签)
#       └─> APIRouter.route(prompt, contact_tier, context)
#               └─> 选择对应 Adapter（deepseek / doubao / openai / custom）
#                       └─> 返回 GenerationResult
#
# 主要类/函数（待实现）：
#
#   class RoutingConfig
#       — 从 config/models.yaml 加载的路由规则配置对象
#       — 字段：business_model, intimate_model, default_model, fallback_model
#
#   class GenerationResult
#       — 统一的模型响应数据结构
#       — 字段：text, model_id, latency_ms, token_usage, error
#
#   class APIRouter
#       def __init__(config: RoutingConfig)
#           — 初始化所有 Adapter 实例，建立路由映射表
#
#       async def route(
#           prompt: str,
#           contact_tier: ContactTier,
#           context: dict
#       ) -> GenerationResult
#           — 核心路由函数：根据 tier 选择 Adapter，发起请求，返回统一结果
#
#       def _select_adapter(tier: ContactTier) -> BaseAdapter
#           — 内部路由逻辑：从映射表中取出对应的 Adapter 实例
#
#       async def _execute_with_retry(
#           adapter: BaseAdapter,
#           payload: dict,
#           max_retries: int = 2
#       ) -> GenerationResult
#           — 带重试与超时的请求执行器
#
#       def register_custom_adapter(name: str, adapter: BaseAdapter) -> None
#           — 允许用户注册自定义 Adapter（扩展点）
#
# 依赖：
#   - brain/api_hub/adapters/            （各模型适配器）
#   - brain/api_hub/config.py            （API Key 与 Base URL 管理）
#   - core/identity/contact_classifier.py （ContactTier 枚举）
#   - config/models.yaml                 （用户配置的路由规则）
#
# 注意事项：
#   - 所有请求均为异步（async/await），避免阻塞 UI 线程
#   - API Key 仅在内存中持有，不写入日志
#   - 路由失败时降级到 fallback_model，保证 Ghost Text 始终有内容输出
# =============================================================================
