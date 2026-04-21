# probe/macos/vision_ocr_probe.py
# ─────────────────────────────────────────────────────────────────────────────
# 模块职责：macOS Vision Framework OCR 探针（备选方案）
# ─────────────────────────────────────────────────────────────────────────────
#
# 使用场景：
#   当 Accessibility API 无法读取微信输入框内容时（如辅助功能权限被拒、
#   微信版本升级导致控件树结构变化），启用本模块作为备选探针。
#   通过截取微信输入区域的屏幕截图，使用 macOS 原生 Vision Framework
#   进行硬件加速 OCR 识别，提取当前输入框文字。
#
# 技术路径（PRD 第三章）：
#   macOS 备选路径：Vision Framework 硬件加速 OCR
#
# 核心流程：
#   1. 确定微信输入框在屏幕上的精确坐标区域（Rect）
#      └─> 通过 Quartz / AppKit 窗口枚举获取微信窗口位置
#   2. 截取目标区域的屏幕截图（CGImage）
#      └─> 使用 CoreGraphics.CGWindowListCreateImage 进行局部截图
#   3. 调用 Vision.VNRecognizeTextRequest 对截图执行 OCR
#      └─> 使用 zh-Hans + en-US 语言模型，硬件加速（GPU/ANE）
#   4. 解析 VNRecognizedTextObservation，提取置信度最高的文本结果
#   5. 返回当前输入框内容字符串，供 GhostText 渲染使用
#
# 与 Accessibility 探针的对比：
#   ┌──────────────────────┬──────────────────┬──────────────────┐
#   │ 维度                 │ Accessibility    │ Vision OCR       │
#   ├──────────────────────┼──────────────────┼──────────────────┤
#   │ 精确度               │ 高（直接读文本） │ 中（OCR 误差）   │
#   │ 实时性               │ 高               │ 中（截图延迟）   │
#   │ 权限要求             │ 辅助功能权限     │ 屏幕录制权限     │
#   │ 微信版本兼容性       │ 依赖控件树结构   │ 高（图像输入）   │
#   │ 性能开销             │ 低               │ 中（Vision 推理）│
#   └──────────────────────┴──────────────────┴──────────────────┘
#
# 主要类与方法（待实现）：
#
#   class VisionOCRProbe(BaseProbe)
#       — 继承 probe/base_probe.py 定义的只读探针基类
#
#       def __init__(self, target_app: str = "WeChat")
#           — 初始化探针，指定目标应用名称
#           — 检查屏幕录制权限，未授权时提示用户引导
#
#       def locate_input_region(self) -> CGRect
#           — 枚举屏幕窗口，定位微信主窗口
#           — 根据微信 UI 布局估算输入框区域坐标
#           — 返回输入框的 CGRect（x, y, width, height）
#           — TODO: 输入框位置可能随微信版本变化，需支持自动校准
#
#       def capture_region(self, region: CGRect) -> CGImage
#           — 调用 CoreGraphics.CGWindowListCreateImage 截取指定区域
#           — 截图仅保存在内存中，不写入磁盘
#           — 截图分辨率应配合 Retina 屏幕的像素密度（@2x）
#
#       def run_ocr(self, image: CGImage) -> str
#           — 创建 VNImageRequestHandler 与 VNRecognizeTextRequest
#           — 配置识别语言：["zh-Hans", "zh-Hant", "en-US"]
#           — 设置识别级别：VNRequestTextRecognitionLevel.accurate
#           — 执行识别请求并返回置信度最高的文本行合并结果
#
#       def read_input_text(self) -> str
#           — 对外暴露的主接口，封装完整的 locate → capture → OCR 流程
#           — 对应 BaseProbe.read_input_text() 抽象方法
#           — 如过程中任意步骤失败，返回空字符串并记录 warning 日志
#
#       def on_permission_denied(self) -> None
#           — 屏幕录制权限被拒时的处理：
#             向 UI 层发送权限引导通知，提示用户前往系统偏好设置授权
#
# 性能优化策略：
#   - 防抖（Debounce）：OCR 调用频率不超过 2 次/秒，避免频繁截图
#   - 差异检测：对比前后两帧截图的哈希值，内容不变时跳过 OCR
#   - 缓存：相同截图内容复用上一次 OCR 结果，减少 Vision 推理次数
#
# 权限说明（用户需手动授权）：
#   系统偏好设置 → 安全性与隐私 → 隐私 → 屏幕录制 → 勾选 Social Copilot
#
# 依赖：
#   - pyobjc-framework-Quartz   （截图 / 窗口枚举）
#   - pyobjc-framework-Vision   （OCR 识别）
#   - probe/base_probe.py       （只读探针基类）
#
# 注意事项：
#   - 严格只读：本模块只截图、只识别文字，绝不向微信窗口写入任何内容
#   - 截图数据仅在内存中流转，识别完成后立即释放，不持久化
#   - 本模块仅在 macOS 12+ 上运行（Vision Framework 中文 OCR 质量要求）
# ─────────────────────────────────────────────────────────────────────────────
