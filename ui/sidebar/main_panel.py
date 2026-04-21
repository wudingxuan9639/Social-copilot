# ui/sidebar/main_panel.py
# =============================================================================
# 主侧边栏面板 (Main Sidebar Panel)
# 对应 PRD 第 4 章 — UI 文本框架布局 (Text Framework)
# =============================================================================
#
# 模块职责：
#   渲染挂载于微信窗口侧边的极客风格分栏 GUI。
#   本面板是整个工具的视觉入口，聚合所有子组件的展示逻辑。
#
# 面板布局（从上到下）：
#   ┌─────────────────────────────────────┐
#   │  ① 状态栏 (StatusBar)               │  ← 当前联系人 / 场景标签 / 模型指示灯
#   ├─────────────────────────────────────┤
#   │  ② 建议卡片区 (SuggestionCards)     │  ← AI 生成的 2-3 条候选回复
#   │     [建议 A]  [建议 B]  [建议 C]    │
#   ├─────────────────────────────────────┤
#   │  ③ 幽灵文本预览 (GhostTextPreview)  │  ← 实时跟随输入框的浅灰色补全内容
#   ├─────────────────────────────────────┤
#   │  ④ 语气切换栏 (ToneSelector)        │  ← 专业 · 亲和 · 极简 三档快切
#   ├─────────────────────────────────────┤
#   │  ⑤ 快捷操作栏 (ActionBar)           │  ← 刷新建议 / 打开设置 / 反馈按钮
#   └─────────────────────────────────────┘
#
# 交互设计原则（来自 PRD）：
#   - 只读不写：侧边栏从不直接修改微信输入框，仅提供建议
#   - Tab 键决策：用户在微信输入框按 Tab 采纳当前幽灵文本建议
#   - 极客风格：深色主题、等宽字体、最小化视觉噪音
#   - 非侵入式：不遮挡微信主窗口，可调节宽度，可折叠
#
# 主要类/组件（待实现）：
#
#   class SocialCopilotSidebar(QWidget)
#       — 侧边栏主窗口类，继承 PyQt6 QWidget
#
#       核心方法：
#         __init__(parent=None)
#             初始化布局、注册信号槽、连接 probe 层事件
#
#         setup_ui() -> None
#             构建所有子组件并设置布局（QVBoxLayout）
#
#         update_suggestions(results: list[SuggestionCard]) -> None
#             接收 brain/api_hub/router.py 返回的生成结果并刷新卡片区
#
#         update_ghost_text(partial: str) -> None
#             更新幽灵文本预览区内容（由 probe 层回调触发）
#
#         on_tone_changed(tone: TonePreset) -> None
#             语气档位变更时，重新请求 AI 建议并刷新卡片
#
#         on_contact_changed(contact_id: str) -> None
#             联系人切换时，更新状态栏标签并清空旧建议
#
#         toggle_panel() -> None
#             折叠 / 展开侧边栏（快捷键触发）
#
#         on_feedback(suggestion_id: str, action: str) -> None
#             接收用户对建议的反馈（采纳 / 拒绝），
#             并将事件路由至 core/reflection/diff_tracker.py
#
# 子组件依赖（各自独立模块）：
#   ui/sidebar/ghost_text.py     — 幽灵文本渲染组件
#   ui/settings/tone_selector.py — 语气选择器组件
#   ui/settings/api_config_panel.py — API 设置入口
#
# 上游数据来源：
#   probe/macos/accessibility_probe.py  — 输入框内容变更事件
#   brain/api_hub/router.py             — AI 生成结果
#   core/identity/contact_classifier.py — 联系人标签
#
# 下游输出：
#   用户采纳的建议文本 → 复制到剪贴板 / Tab 键写入输入框（由操作系统 API 完成）
#   用户反馈事件      → core/reflection/diff_tracker.py
#
# 技术选型：
#   GUI 框架：PyQt6（QWidget + QVBoxLayout）
#   主题：深色 QSS 样式表（极客风格，配色参考 VS Code Dark+）
#   字体：JetBrains Mono / SF Mono（等宽字体）
#
# TODO（开发阶段二）:
#   [ ] 实现 SocialCopilotSidebar 主类骨架
#   [ ] 实现窗口跟随微信主窗口位置移动的逻辑
#   [ ] 实现深色 QSS 主题样式表
#   [ ] 实现建议卡片组件（SuggestionCard Widget）
#   [ ] 实现折叠/展开动画
#   [ ] 接入 probe 层事件总线
# =============================================================================
