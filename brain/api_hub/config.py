# brain/api_hub/config.py
# ─────────────────────────────────────────────────────────────────────────────
# 模块职责：BYOK API 配置管理器
# ─────────────────────────────────────────────────────────────────────────────
#
# 负责加载、校验并暴露用户自定义的 API 接入配置。
# 所有 API Key 均存储在用户本地，软件不进行任何上报。
#
# 配置来源（优先级从高到低）：
#   1. 环境变量（.env 文件）
#   2. config/models.yaml
#   3. UI 设置面板的用户输入（写回 models.yaml）
#
# 配置结构示意（参考 config/models.yaml）：
#   models:
#     business:
#       provider: deepseek
#       base_url: https://api.deepseek.com/v1
#       api_key: sk-...
#       model_name: deepseek-chat
#       max_tokens: 512
#     intimate:
#       provider: doubao
#       base_url: https://ark.cn-beijing.volces.com/api/v3
#       api_key: ...
#       model_name: doubao-pro-32k
#       max_tokens: 256
#     default:
#       provider: openai_compatible
#       base_url: https://api.openai.com/v1
#       api_key: sk-...
#       model_name: gpt-4o-mini
#       max_tokens: 512
#
# 主要数据结构（待实现）：
#   class ModelConfig         — 单个模型的接入配置（base_url / api_key / model_name）
#   class HubConfig           — 全量配置，包含多场景模型映射表
#
# 主要函数（待实现）：
#   load_config(path: str) -> HubConfig
#       从 models.yaml 读取并校验配置，返回 HubConfig 对象
#
#   save_config(config: HubConfig, path: str) -> None
#       将用户在 UI 面板中修改的配置回写到 models.yaml
#
#   validate_api_key(model_config: ModelConfig) -> bool
#       向对应 base_url 发送探测请求，验证 API Key 有效性
#
#   get_model_for_scenario(scenario: str) -> ModelConfig
#       根据场景标签（business / intimate / default）返回对应 ModelConfig
#
# 安全注意事项：
#   - API Key 在内存中以 SecretStr 类型持有，禁止打印或写入日志
#   - models.yaml 中的密钥字段应支持从环境变量引用（如 ${DEEPSEEK_API_KEY}）
#   - config/ 目录下的 secrets.yaml 已加入 .gitignore，防止密钥泄露
# ─────────────────────────────────────────────────────────────────────────────
