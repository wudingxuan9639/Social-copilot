# 2.2 人设一致性与语气灵活切换 (Tone Mask)
#
# 职责：
#   - persona_manager  : 维护用户核心人设（身份底色），跨会话保持稳定
#   - tone_filter      : 语气滤镜，提供「专业 / 亲和 / 极简」等切换方案
#
# 设计原则：
#   身份底色（Who I Am）永远不变，只有表达方式（How I Say It）随场景浮动。
