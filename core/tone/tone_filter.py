# tone_filter.py
# 模块职责：语气滤镜（Tone Filter）
# -----------------------------------------------
# 在保持用户核心人设不变的前提下，对 AI 生成的建议文本
# 应用"专业 / 亲和 / 极简"等预设语气风格。
#
# 主要职责：
#   - 接收 persona_manager 输出的原始建议文本
#   - 根据用户在 UI 中选择的语气档位，对文本进行风格转换
#   - 输出风格化后的建议文本供 ghost_text 渲染
#
# 预设语气档位（Tone Preset）：
#   - PROFESSIONAL : 正式、简洁、逻辑优先，适合商务场景
#   - WARM         : 亲切、口语化、带情绪共鸣，适合亲密场景
#   - MINIMAL      : 极简回复，字数压缩至最短，适合低能量状态
#
# 依赖：
#   - core/tone/persona_manager.py  （获取稳定人设底色）
#   - brain/scenario/detector.py    （可选：自动推荐匹配的语气档位）
#
# 待实现：
#   class ToneFilter
#       def apply(raw_text: str, tone: TonePreset) -> str
#       def list_presets() -> list[TonePreset]
#       def get_active_tone() -> TonePreset
#       def set_active_tone(tone: TonePreset) -> None
