# module: core/tone/persona_manager.py
# 职责：核心人设管理器 (Persona Manager)
#
# 对应 PRD 2.2 — 人设一致性与语气灵活切换 (Tone Mask)
# 无论用户在回复哪位联系人，其专业背景与核心身份标签始终保持稳定。
#
# 主要职责：
#   - 从 myself.skill 文件加载用户的身份底色（职业、专长、个人标签）
#   - 向外暴露只读的 PersonaProfile 数据结构，供 brain 层 Prompt 构造使用
#   - 监听 skill 文件变更，热重载更新后的人设数据
#
# 待实现类与函数：
#   class PersonaProfile        — 用户身份数据类（职业/专长/核心标签列表）
#   class PersonaManager        — 人设管理器主类
#     def load_from_skill()     — 从加密的 myself.skill 文件中反序列化人设
#     def get_profile()         — 返回当前激活的 PersonaProfile 实例
#     def reload()              — 热重载（当 skill 文件更新后调用）
#
# 依赖：
#   core/skill_distiller/encryptor.py  — 用于解密 myself.skill
#   data/skill/                        — myself.skill 文件存储目录
