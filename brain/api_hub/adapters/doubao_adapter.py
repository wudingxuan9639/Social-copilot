# doubao_adapter.py
# ─────────────────────────────────────────────────────────────────────────────
# 模块职责：豆包 (Doubao) 模型适配器
# ─────────────────────────────────────────────────────────────────────────────
#
# 对应 PRD 2.3 — 灵活 API 接入 (Flexible Hub / BYOK)
#
# 豆包（字节跳动 / 火山引擎）API 兼容 OpenAI 协议，
# 本适配器在通用 OpenAI 客户端的基础上，处理豆包特有的：
#   - Base URL 差异（https://ark.cn-beijing.volces.com/api/v3）
#   - 模型 ID 命名规范（endpoint_id 格式）
#   - 速率限制与重试策略
#   - 响应格式的细微差异（如 usage 字段）
#
# 推荐使用场景（来自 PRD）：
#   亲密场景 —— 豆包在拟人化表达、情感共鸣方面表现更优，
#   适合用于 Scenario.INTIMATE 的 Prompt 路由。
#
# 对外接口（待实现）：
#   class DoubaoAdapter(BaseAdapter)
#       def __init__(self, api_key: str, endpoint_id: str)
#           初始化豆包客户端，配置 Base URL 与模型端点 ID
#
#       async def complete(prompt: str, context: dict) -> str
#           发送补全请求，返回纯文本建议内容
#
#       async def stream_complete(prompt: str, context: dict) -> AsyncIterator[str]
#           流式返回补全内容，用于 Ghost Text 实时渲染
#
#       def estimate_tokens(text: str) -> int
#           估算 Token 数量，用于 Prompt 长度控制
#
#       def get_model_info() -> dict
#           返回当前模型端点的元信息（名称、最大上下文长度、价格参考）
#
# 继承关系：
#   DoubaoAdapter → BaseAdapter（见 brain/api_hub/router.py）
#
# 依赖：
#   - openai (>=1.0, 兼容 OpenAI 协议的统一客户端)
#   - brain/api_hub/config.py    （读取 API Key 与 endpoint_id 配置）
#   - brain/api_hub/router.py    （由路由器统一调度，不直接对外暴露）
#
# 配置示例（来自 config/models.yaml）：
#   doubao:
#     base_url: "https://ark.cn-beijing.volces.com/api/v3"
#     endpoint_id: "ep-xxxxxxxx-xxxx"
#     api_key: "${DOUBAO_API_KEY}"   # 从环境变量读取，绝不硬编码
#     max_tokens: 512
#     temperature: 0.85              # 亲密场景适当提高随机性
#
# TODO:
#   - [ ] 继承 BaseAdapter 并实现所有抽象方法
#   - [ ] 添加 exponential backoff 重试逻辑（豆包有 QPS 限制）
#   - [ ] 处理豆包特有的错误码映射
#   - [ ] 添加 Token 计费日志，供用户追踪 API 成本
# ─────────────────────────────────────────────────────────────────────────────
