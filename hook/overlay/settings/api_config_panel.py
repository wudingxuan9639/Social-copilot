# ui/settings/api_config_panel.py
# =============================================================================
# 模块职责：API 配置面板 (API Config Panel)
# 对应 PRD 2.3 — 极致灵活的 API 接入 (Flexible Hub / BYOK)
# =============================================================================
#
# 面板用途：
#   允许用户在 UI 中直接填写和管理各场景下的 AI 模型接入配置，
#   包括 API Key、Base URL、模型名称、温度等参数，
#   无需手动编辑 config/models.yaml 文件。
#
# 面板布局（草图）：
#   ┌─────────────────────────────────────────────────────┐
#   │  🧠  AI 模型配置                              [保存] │
#   ├─────────────────────────────────────────────────────┤
#   │  场景：[商务场景 ▼]                                  │
#   │                                                     │
#   │  服务商：[DeepSeek ▼]                               │
#   │  Base URL：[ https://api.deepseek.com/v1          ] │
#   │  API Key： [ sk-••••••••••••••••••  ] [👁 显示]     │
#   │  模型名称：[ deepseek-chat                        ] │
#   │  温度：    [────●──────] 0.7                        │
#   │  最大 Token：[ 512 ]                                │
#   │                                                     │
#   │  [🔍 测试连接]   状态：✅ 连接正常（延迟 312ms）      │
#   ├─────────────────────────────────────────────────────┤
#   │  场景：[亲密场景 ▼]                                  │
#   │  ... (同上布局，预设为豆包)                          │
#   ├─────────────────────────────────────────────────────┤
#   │  场景：[默认/通用 ▼]                                 │
#   │  ... (同上布局，预设为 OpenAI 兼容协议)              │
#   └─────────────────────────────────────────────────────┘
#
# 主要职责：
#   1. 渲染多场景分 Tab 的 API 配置表单（商务 / 亲密 / 默认）
#   2. 读取 config/models.yaml 并将配置填充到对应表单字段
#   3. 用户修改后，写回 config/models.yaml（调用 brain/api_hub/config.py）
#   4. "测试连接"按钮触发 config.validate_api_key()，实时显示连接状态
#   5. API Key 输入框默认 mask 显示，保护隐私
#   6. 支持一键重置为各服务商的默认参数（Base URL、模型名等）
#
# 主要类与方法（待实现）：
#
#   class APIConfigPanel(QWidget)
#       ├── __init__(parent=None)
#       │       — 初始化 UI 布局，加载当前 models.yaml 配置到表单
#       │
#       ├── _build_layout() -> None
#       │       — 构建面板整体 UI 结构（Tab + Form + Buttons）
#       │
#       ├── _build_model_form(scenario: str) -> QGroupBox
#       │       — 构建单个场景的模型配置表单组件
#       │       — 包含：服务商下拉、Base URL、API Key、模型名、温度滑块、Token 上限
#       │
#       ├── _populate_form(scenario: str, config: ModelConfig) -> None
#       │       — 将 ModelConfig 数据填充到对应场景的表单字段
#       │
#       ├── _read_form(scenario: str) -> ModelConfig
#       │       — 从表单字段读取用户输入，构造 ModelConfig 数据对象
#       │
#       ├── _on_save_clicked() -> None
#       │       — 保存按钮回调：读取所有场景表单 → 写回 models.yaml
#       │
#       ├── _on_test_connection_clicked(scenario: str) -> None
#       │       — 测试连接按钮回调：调用 validate_api_key()，更新状态指示器
#       │
#       ├── _on_provider_changed(provider: str, scenario: str) -> None
#       │       — 服务商下拉切换时，自动填充该服务商的默认 Base URL 与模型名
#       │
#       ├── _toggle_api_key_visibility(scenario: str) -> None
#       │       — 切换 API Key 输入框的明文 / 掩码显示状态
#       │
#       └── refresh() -> None
#               — 外部调用接口：重新从 models.yaml 加载配置并刷新表单
#               — 用于 skill 更新或外部配置变更后的同步
#
# 预设服务商与默认值（PROVIDER_PRESETS）：
#   "deepseek"  : base_url="https://api.deepseek.com/v1",  model="deepseek-chat"
#   "doubao"    : base_url="https://ark.cn-beijing.volces.com/api/v3", model="<endpoint_id>"
#   "openai"    : base_url="https://api.openai.com/v1",    model="gpt-4o-mini"
#   "qwen"      : base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", model="qwen-plus"
#   "custom"    : base_url="",  model=""  ← 完全由用户手动输入
#
# 信号（Qt Signals，待定义）：
#   config_saved    = Signal(HubConfig)   — 配置保存成功后发出，通知 Router 热重载
#   test_started    = Signal(str)         — 测试连接开始（携带 scenario 标签）
#   test_finished   = Signal(str, bool)   — 测试连接结束（场景标签 + 是否成功）
#
# 依赖：
#   - PyQt6                            — UI 框架
#   - brain/api_hub/config.py          — ModelConfig / HubConfig 数据类 + 配置读写
#   - brain/api_hub/router.py          — 配置保存后通知 Router 热重载
#   - config/models.yaml               — 用户配置持久化文件
#
# 注意事项：
#   - API Key 字段严禁写入日志或控制台输出
#   - 配置保存前需做基础校验（URL 格式合法、Key 非空）
#   - 保存操作应支持 undo（保留上一份配置快照，以便"测试后发现不可用"时回滚）
# =============================================================================
