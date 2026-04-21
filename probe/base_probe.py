# probe/base_probe.py
# =============================================================================
# 模块职责：屏幕探针基类 (Base Probe)
# =============================================================================
#
# 设计原则（来自 PRD 第 3 章）：
#   只读不写。不修改微信内存，不侵入协议层，
#   仅通过辅助功能 API 或截图方式对微信界面进行"旁观"。
#
# 本基类定义了所有平台探针（macOS / Windows）必须实现的统一接口契约。
# 具体实现位于各平台子目录：
#   probe/macos/accessibility_probe.py  — macOS Accessibility API 实现
#   probe/macos/vision_ocr_probe.py     — macOS Vision Framework OCR 备选实现
#   probe/windows/uiautomation_probe.py — Windows UIAutomation 实现
#
# 数据流：
#   BaseProbe.get_input_text()
#       └─> 返回用户当前在微信输入框中已输入的文本片段
#               └─> brain/api_hub/router.py（触发补全请求）
#
#   BaseProbe.get_conversation_context()
#       └─> 返回当前对话窗口最近 N 条消息
#               └─> brain/scenario/detector.py（场景识别）
#
# =============================================================================
#
# 待实现的抽象方法：
#
#   get_input_text() -> str
#       读取微信输入框内当前已输入的文本内容（实时，低延迟）
#       返回空字符串表示输入框为空或无法读取
#
#   get_conversation_context(limit: int) -> list[dict]
#       读取当前对话窗口中最近 limit 条消息
#       每条消息格式：
#         { "direction": "sent" | "received", "text": str, "timestamp": str }
#
#   get_active_contact() -> dict | None
#       读取当前微信窗口正在聊天的联系人信息
#       返回格式：{ "id": str, "display_name": str }
#       无法识别时返回 None
#
#   is_wechat_focused() -> bool
#       检测微信窗口当前是否处于前台焦点状态
#       用于决定是否激活 Ghost Text 渲染
#
#   start_listening(callback: Callable[[ProbeEvent], None]) -> None
#       启动后台监听，当输入框内容发生变化时触发 callback
#       callback 接收一个 ProbeEvent 对象（见下方数据结构说明）
#
#   stop_listening() -> None
#       停止后台监听，释放相关系统资源
#
# =============================================================================
#
# ProbeEvent 数据结构（待定义）：
#   ProbeEvent:
#     event_type    : Literal["input_changed", "contact_switched", "message_received"]
#     input_text    : str          — 当前输入框文字（event_type == "input_changed" 时有效）
#     contact       : dict | None  — 当前联系人信息
#     timestamp     : datetime     — 事件发生时间
#     raw_snapshot  : Any | None   — 平台原始数据（调试用，生产环境可为 None）
#
# =============================================================================
#
# 继承示例：
#
#   from probe.base_probe import BaseProbe, ProbeEvent
#
#   class AccessibilityProbe(BaseProbe):
#       def get_input_text(self) -> str:
#           # 通过 macOS Accessibility API 读取输入框
#           ...
#
#       def get_conversation_context(self, limit: int = 5) -> list[dict]:
#           # 遍历微信对话列表控件，提取最近 N 条消息
#           ...
#
# =============================================================================
#
# 平台探针选择逻辑（probe/__init__.py 中实现）：
#   import sys
#   if sys.platform == "darwin":
#       from probe.macos.accessibility_probe import AccessibilityProbe as Probe
#   elif sys.platform == "win32":
#       from probe.windows.uiautomation_probe import UIAutomationProbe as Probe
#   else:
#       raise NotImplementedError("当前平台暂不支持")
#
# =============================================================================
#
# 注意事项：
#   - 所有探针实现必须是异步友好的（不得长时间阻塞主线程）
#   - 探针读取的数据不得持久化到磁盘（内存临时使用后即释放）
#   - 若读取权限不足（如用户未授权辅助功能），应抛出 ProbePermissionError
#     并在 UI 层引导用户前往系统设置完成授权
# =============================================================================
