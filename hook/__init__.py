"""
probe — 感知层：非侵入式屏幕捕获探针 (Non-Intrusive Screen Probe)

核心原则：只读不写。
  本层通过系统级辅助功能 API 或截图 OCR，以旁观者身份读取微信窗口内容，
  绝不修改微信进程内存、不注入代码、不侵入通信协议。

支持平台：
  macOS   — 首选 Accessibility API，备选 Vision Framework OCR
  Windows — 首选 UIAutomation 控件树遍历

子模块：
  base_probe.py       — 探针抽象基类，定义统一的只读接口契约
  macos/
    accessibility_probe.py  — macOS Accessibility API 实现（读取文本控件）
    vision_ocr_probe.py     — macOS Vision Framework OCR 备选实现
  windows/
    uiautomation_probe.py   — Windows UIAutomation 控件树实现

数据流：
  微信窗口（只读）
      └─> Probe.get_current_context()
              └─> ConversationContext { contact, messages, input_text }
                      └─> brain/scenario/detector.py（场景识别）
                      └─> ui/sidebar/ghost_text.py（触发补全渲染）

设计约束：
  - 所有探针实现必须继承 BaseProbe，保证接口一致性
  - 捕获频率需做节流控制（debounce），避免 CPU 占用过高
  - 捕获内容仅在内存中短暂存留，不持久化到磁盘
  - 必须在用户明确授权辅助功能权限后方可启动
"""

from .base_probe import BaseProbe

__all__ = ["BaseProbe"]
