# 本地灵魂蒸馏器 (Skill Distiller)
# ================================
# 第一阶段核心模块：扫描本地微信聊天记录，提取用户的表达特征、
# 高频用语、专业背景，生成加密的 myself.skill 文件。
#
# 子模块说明：
#   parser.py           — 微信数据库 / 导出文件解析器
#   feature_extractor.py — 高频词、语气词、惯用句式特征提取
#   skill_builder.py    — 将特征聚合，序列化为 myself.skill (JSON)
#   encryptor.py        — 本地 AES 加密 / 解密，保护隐私数据
