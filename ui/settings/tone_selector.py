# ui/settings/tone_selector.py
# ─────────────────────────────────────────────────────────────────────────────
# 模块职责：语气档位选择器 UI 组件 (Tone Selector)
# ─────────────────────────────────────────────────────────────────────────────
#
# 对应 PRD 2.2 — 人设一致性与语气灵活切换 (Tone Mask)
#
# 概述：
#   在侧边栏设置面板中提供一个轻量的语气切换控件，
#   让用户无需离开当前对话窗口即可一键切换 AI 建议的语气风格。
#   切换操作不影响用户的核心人设（身份底色），仅改变表达方式。
#
# 三档语气预设（Tone Preset）：
#   ┌────────────────┬──────────────────────────────────────────────────────┐
#   │  档位           │  适用场景与表现                                       │
#   ├────────────────┼──────────────────────────────────────────────────────┤
#   │  PROFESSIONAL  │  正式商务场景。简洁有力，逻辑优先，无 Emoji，无口语    │
#   │  WARM          │  亲密日常场景。口语化，情绪共鸣，可用呢称与 Emoji      │
#   │  MINIMAL       │  低能量 / 快速回复。极简一句话，字数压缩至最短         │
#   └────────────────┴──────────────────────────────────────────────────────┘
#
# UI 控件形态（建议实现为三态 Toggle 或 SegmentedControl）：
#   [ 专业 ]  [ 亲和 ]  [ 极简 ]
#     ▲ 当前选中态以高亮颜色标注（极客风格：青色 / 绿色 accent）
#
# 与其他模块的交互：
#   - 读取：core/tone/tone_filter.py → 获取当前激活档位，渲染默认选中态
#   - 写入：用户点击后调用 tone_filter.set_active_tone(preset)，实时生效
#   - 联动：tone 切换后，ui/sidebar/ghost_text.py 应立即刷新候选建议
#
# 主要类与方法（待实现）：
#
#   class TonePreset(enum.Enum)
#       PROFESSIONAL = "professional"
#       WARM         = "warm"
#       MINIMAL      = "minimal"
#
#       def label(self) -> str
#           返回用于 UI 显示的中文标签（"专业" / "亲和" / "极简"）
#
#       def description(self) -> str
#           返回档位的简短说明文字（用于悬停 Tooltip）
#
#   class ToneSelectorWidget(QWidget)  # 基于 PyQt6
#       ├── __init__(parent, tone_filter: ToneFilter)
#       │       — 初始化三态切换控件，绑定 ToneFilter 实例
#       │       — 从 tone_filter.get_active_tone() 读取初始选中态
#       │
#       ├── _build_ui() -> None
#       │       — 构建 SegmentedControl 样式的三按钮布局
#       │       — 应用极客风格 QSS（深色背景，青色 active 态）
#       │
#       ├── _on_preset_clicked(preset: TonePreset) -> None
#       │       — 点击事件处理器：更新选中态，调用 ToneFilter.set_active_tone()
#       │       — 发出 tone_changed 信号，通知 GhostTextWidget 刷新
#       │
#       ├── tone_changed = pyqtSignal(TonePreset)
#       │       — Qt 信号：语气档位变更事件，供 sidebar/ghost_text.py 订阅
#       │
#       └── set_enabled_presets(presets: list[TonePreset]) -> None
#               — 允许根据当前联系人场景动态禁用某些档位
#               — 例如：亲密场景下自动禁用 PROFESSIONAL，并附提示文字
#
# 样式规范（极客风格 QSS，配合 sidebar 整体设计）：
#   背景色：#1E1E2E（深紫黑）
#   默认态：#3A3A4E（灰紫）
#   激活态：#00FFB2（青绿 accent）
#   字体：JetBrains Mono 或系统等宽字体，12px
#   圆角：4px
#   边距：4px 间距，整体控件高度 28px
#
# 依赖：
#   - PyQt6                        — UI 框架
#   - core/tone/tone_filter.py     — 语气滤镜逻辑层
#   - ui/sidebar/ghost_text.py     — 订阅 tone_changed 信号
#
# TODO:
#   [ ] 实现 TonePreset 枚举与标签映射
#   [ ] 实现 ToneSelectorWidget 三态按钮 UI
#   [ ] 添加 Tooltip 展示各档位说明
#   [ ] 支持键盘快捷键切换（如 Ctrl+1/2/3）
#   [ ] 记忆用户的上次选择，下次启动时恢复
# ─────────────────────────────────────────────────────────────────────────────
