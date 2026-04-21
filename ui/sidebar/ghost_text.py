# ui/sidebar/ghost_text.py
# =============================================================================
# 模块职责：幽灵文本渲染器 (Ghost Text Renderer)
# 对应 PRD 2.6 — 智能辅助补全交互 (Ghost Text & Tab)
# =============================================================================
#
# 核心交互设计：
#   当用户在微信输入框打出半句话时，本模块将 AI 预测的补全内容
#   以"浅灰色幽灵文字"的形式渲染在侧边栏预览区（而非直接写入微信输入框）。
#   用户按下 Tab 键后，补全内容被复制到剪贴板或通过 UI 呈现供用户一键采纳。
#
# 渲染原则（对应 PRD 核心哲学"只读不写，人工决策"）：
#   ✦ 不侵入微信输入框：幽灵文本仅显示在侧边栏，不修改任何微信控件
#   ✦ 浅灰色样式标识"待采纳"状态，与已确认内容形成视觉区分
#   ✦ Tab 键 = 用户主动决策采纳，不强制、不自动写入
#
# 渲染状态机：
#   IDLE         → 用户未输入 / 无补全内容
#   LOADING      → 正在请求 AI 补全（显示加载动画）
#   PREVIEW      → 补全结果已就绪，幽灵文本可见，等待用户决策
#   ACCEPTED     → 用户按 Tab 采纳，文本复制到剪贴板，UI 高亮确认
#   DISMISSED    → 用户继续输入或按 Esc 忽略，清除幽灵文本
#
# 主要职责：
#   1. 接收来自 brain/api_hub/router.py 的流式或完整补全文本
#   2. 在侧边栏预览区以浅灰色字体渲染候选回复
#   3. 监听 Tab 键事件，触发"采纳"动作（复制到剪贴板）
#   4. 监听 Esc 键或用户继续输入事件，触发"忽略"动作
#   5. 支持流式渲染（Streaming）：逐 token 更新，提升体验流畅感
#   6. 提供"接受 / 忽略 / 改写"三个操作按钮（UI 扩展）
#
# 与其他模块的数据交互：
#
#   probe/（输入监听）
#       └─> 用户当前输入的半句话（partial_input）
#               └─> GhostTextRenderer.on_input_change(text: str)
#
#   brain/api_hub/router.py（补全生成）
#       └─> AI 返回的补全文本流（stream: AsyncIterator[str]）
#               └─> GhostTextRenderer.start_stream(stream)
#
#   ui/tab_handler.py（Tab 键采纳）
#       └─> TabHandler 触发 GhostTextRenderer.accept()
#
#   core/reflection/diff_tracker.py（反思记录）
#       └─> 用户采纳时，记录 draft（AI草稿）和 final（用户终稿）
#
# 主要类与方法（待实现）：
#
#   class GhostTextState(Enum)
#       IDLE / LOADING / PREVIEW / ACCEPTED / DISMISSED
#
#   class GhostTextRenderer(QWidget)        ← 继承 PyQt6 的 QWidget
#       ├── __init__(parent=None)
#       │       — 初始化侧边栏预览组件，设置浅灰色字体样式
#       │
#       ├── on_input_change(partial_input: str) -> None
#       │       — probe 层回调：用户输入内容变更，触发 AI 补全请求
#       │       — 内置防抖（debounce 300ms），避免频繁触发 API 调用
#       │
#       ├── start_stream(stream: AsyncIterator[str]) -> None
#       │       — 接收流式补全文本，逐 token 更新预览区内容
#       │       — 状态切换：IDLE → LOADING → PREVIEW
#       │
#       ├── set_preview(text: str) -> None
#       │       — 非流式模式：直接设置完整补全文本
#       │       — 以浅灰色（#AAAAAA）渲染在预览文本框中
#       │
#       ├── accept() -> str
#       │       — 用户按 Tab 采纳：将当前幽灵文本复制到系统剪贴板
#       │       — 状态切换：PREVIEW → ACCEPTED
#       │       — 触发 diff_tracker 记录采纳事件
#       │       — 返回已采纳的文本内容
#       │
#       ├── dismiss() -> None
#       │       — 用户忽略：清空预览区，重置状态为 IDLE
#       │       — 触发 diff_tracker 记录"拒绝"事件（用于 Reflection Loop）
#       │
#       ├── clear() -> None
#       │       — 清空所有预览内容，状态重置为 IDLE
#       │
#       ├── set_loading(is_loading: bool) -> None
#       │       — 切换加载动画显示（三个跳动点 或 进度条）
#       │
#       ├── get_state() -> GhostTextState
#       │       — 返回当前渲染器状态
#       │
#       └── _apply_ghost_style(text: str) -> str
#               — 内部方法：将文本包装为浅灰色富文本 HTML（供 QLabel 渲染）
#               — 示例输出：<span style="color: #AAAAAA; font-style: italic;">...</span>
#
# UI 样式规范：
#   ┌─────────────────────────────────────────────────────────┐
#   │  幽灵文本区域样式                                         │
#   │  ─────────────────────────────────────────────────────  │
#   │  背景色：与侧边栏主背景一致（深色模式 #1E1E1E）            │
#   │  字体颜色：浅灰 #AAAAAA（正常文本为 #FFFFFF）             │
#   │  字体样式：斜体（italic），区分于用户已输入的正常文字       │
#   │  字号：与微信输入框字号一致，保持视觉连贯                  │
#   │  动画：流式渲染时，末尾光标闪烁（0.5s 频率）              │
#   └─────────────────────────────────────────────────────────┘
#
# 键盘快捷键：
#   Tab     → accept()     采纳当前幽灵文本
#   Esc     → dismiss()    忽略，清除幽灵文本
#   ↑ / ↓  → （预留）在多条建议候选之间切换
#
# 依赖：
#   - PyQt6                        （UI 框架）
#   - brain/api_hub/router.py      （获取补全文本流）
#   - ui/tab_handler.py            （Tab 键事件绑定）
#   - core/reflection/diff_tracker.py  （采纳/拒绝事件记录）
#
# TODO（Phase 2 开发重点）：
#   - [ ] 实现 GhostTextState 状态枚举
#   - [ ] 实现带防抖的 on_input_change 回调
#   - [ ] 实现 start_stream 的 asyncio 与 PyQt6 事件循环桥接
#   - [ ] 实现 accept() 的剪贴板写入逻辑
#   - [ ] 设计并实现"3条候选回复"展示 UI（优先级较低）
#   - [ ] 添加单元测试（mock 流式数据）
# =============================================================================
