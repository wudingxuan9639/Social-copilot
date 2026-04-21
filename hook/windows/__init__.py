# probe/windows — Windows 平台屏幕捕获探针包
# =============================================
# 对应 PRD 第三章：屏幕捕获技术方案（Windows 路径）
#
# 技术方案：
#   首选：UIAutomation API
#     - 遍历微信窗口的控件树（Automation Element Tree）
#     - 精准定位聊天消息列表控件与输入框控件
#     - 直接读取控件文本属性，无需 OCR，延迟极低
#
#   备选：GDI 截图 + OCR
#     - 当 UIAutomation 无法穿透微信自绘控件时启用
#     - 使用 Pillow 截取微信窗口区域
#     - 接入 Windows.Media.Ocr 或第三方 OCR 引擎识别文字
#
# 子模块：
#   uiautomation_probe.py  — 基于 UIAutomation 的控件树遍历探针（主方案）
#
# 设计原则：
#   - 严格只读，不向微信进程写入任何数据
#   - 不注入 DLL，不 Hook 任何系统调用
#   - 所有操作通过 Windows 辅助功能（Accessibility）合规接口完成
#
# 依赖：
#   uiautomation  (pip install uiautomation)
#   Pillow        (pip install Pillow，截图备选方案)
#
# 平台要求：
#   仅在 Windows 10 / 11 环境下运行
#   需开启系统"辅助功能"权限
