# ui/tab_handler.py
# ─────────────────────────────────────────────────────────────────────────────
# 模块职责：Tab 键采纳逻辑处理器 (Tab Key Decision Handler)
# 对应 PRD 2.6 — 智能辅助补全交互 (Ghost Text & Tab)
# ─────────────────────────────────────────────────────────────────────────────
#
# 核心交互流程：
#   1. probe 层捕获用户在微信输入框的实时输入（partial_text）
#   2. brain 层异步生成补全建议，ghost_text.py 渲染为浅灰色预览
#   3. 用户按下 Tab 键 → TabHandler 触发采纳逻辑
#   4. 采纳后：
#      a. 将建议文本写入剪贴板（用户自行粘贴，保持"只读不写"原则）
#      b. 或：调用辅助功能 API 将文本注入输入框（可选，需用户授权）
#      c. 清除 Ghost Text 预览
#      d. 向 Reflection Loop 发送「已采纳」信号
#   5. 用户按 Esc 或继续输入 → 触发「拒绝」逻辑，向 Reflection Loop 发送「已拒绝」信号
#
# 关键设计决策：
#   ┌────────────────┬────────────────────────────────────────────────────┐
#   │ 事件           │ 处理逻辑                                            │
#   ├────────────────┼────────────────────────────────────────────────────┤
#   │ Tab 按下       │ 采纳建议 → 复制到剪贴板 → 清除 Ghost Text           │
#   │ Esc 按下       │ 拒绝建议 → 清除 Ghost Text → 触发 diff_tracker      │
#   │ 继续输入       │ 拒绝建议 → 触发新一轮 AI 补全请求                    │
#   │ 切换联系人     │ 清除所有状态 → 重置 Ghost Text                       │
#   └────────────────┴────────────────────────────────────────────────────┘
#
# 「只读不写」原则说明：
#   本工具的核心原则是不主动修改任何应用的内容。
#   Tab 键采纳后的默认行为是将文本复制到系统剪贴板，
#   由用户手动粘贴（Cmd+V / Ctrl+V）完成输入。
#   如用户在设置中明确开启「自动注入」权限，则可通过
#   Accessibility API 直接将文本写入微信输入框。
#
# 主要类与函数（待实现）：
#
#   class AcceptanceMode(Enum)
#       CLIPBOARD   — 采纳后复制到剪贴板（默认，非侵入）
#       AUTO_INJECT — 采纳后自动注入输入框（需用户开启 Accessibility 权限）
#
#   class TabHandlerEvent(Enum)
#       ACCEPTED    — 用户按下 Tab，采纳建议
#       REJECTED    — 用户按下 Esc，拒绝建议
#       OVERRIDDEN  — 用户继续手动输入，隐式拒绝建议
#       EXPIRED     — 建议超时未操作（超过 N 秒自动消失）
#
#   class TabHandler
#       def __init__(
#           self,
#           ghost_text_renderer,       # ui/sidebar/ghost_text.py 实例
#           reflection_tracker,        # core/reflection/diff_tracker.py 实例
#           acceptance_mode: AcceptanceMode = AcceptanceMode.CLIPBOARD
#       )
#
#       def on_tab_pressed(
#           self,
#           current_suggestion: str,
#           contact_id: str,
#           draft_text: str
#       ) -> None
#           — Tab 键按下的主处理函数
#           — 执行采纳流程（剪贴板 / 注入），清除 Ghost Text，发送采纳事件
#
#       def on_esc_pressed(
#           self,
#           current_suggestion: str,
#           contact_id: str,
#           draft_text: str
#       ) -> None
#           — Esc 键按下处理函数
#           — 清除 Ghost Text，发送拒绝事件给 Reflection Loop
#
#       def on_user_continued_typing(
#           self,
#           new_partial: str,
#           contact_id: str
#       ) -> None
#           — 用户继续输入时触发
#           — 隐式拒绝旧建议，向 brain 层发起新一轮补全请求
#
#       def on_contact_switched(self, new_contact_id: str) -> None
#           — 联系人切换时触发
#           — 清除当前所有 Ghost Text 与状态，重置会话上下文
#
#       def _copy_to_clipboard(self, text: str) -> None
#           — 将采纳的建议文本写入系统剪贴板
#
#       def _inject_to_input_box(self, text: str) -> None
#           — （仅 AUTO_INJECT 模式）通过 Accessibility API 写入微信输入框
#           — 调用 probe/macos/accessibility_probe.py 或 probe/windows/uiautomation_probe.py
#
#       def _emit_event(self, event: TabHandlerEvent, payload: dict) -> None
#           — 向事件总线发送用户决策事件，供以下模块订阅：
#             · core/reflection/diff_tracker.py（记录采纳/拒绝行为）
#             · brain/api_hub/router.py（触发新一轮生成）
#             · ui/sidebar/ghost_text.py（控制显示/隐藏）
#
# 依赖关系：
#   - ui/sidebar/ghost_text.py              （控制幽灵文本显示与清除）
#   - core/reflection/diff_tracker.py       （发送用户决策反馈）
#   - brain/api_hub/router.py               （触发新一轮 AI 补全）
#   - probe/macos/accessibility_probe.py    （AUTO_INJECT 模式下写入输入框）
#   - probe/windows/uiautomation_probe.py   （Windows 平台同上）
#
# TODO:
#   [ ] 实现 TabHandler 主类及所有事件处理方法
#   [ ] 实现跨平台剪贴板写入（macOS: pbcopy / pyperclip，Windows: pyperclip）
#   [ ] 实现全局键盘钩子注册（监听 Tab/Esc，且不干扰其他应用的 Tab 行为）
#   [ ] 建立事件总线机制（可用 Python asyncio.Queue 或轻量级 pubsub 库）
#   [ ] 添加防抖（debounce）逻辑：快速连续按键时只触发最后一次
# ─────────────────────────────────────────────────────────────────────────────
