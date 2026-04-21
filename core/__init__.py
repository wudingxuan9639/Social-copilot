"""
core — 本地底座层 (Local Skill Foundation)

负责所有在用户设备本地运行的能力，不依赖任何外部网络请求。

子模块：
  skill_distiller/  — 灵魂蒸馏器：解析微信语料，提炼用户高频特征，生成 myself.skill
  identity/         — 身份建模：对联系人进行分类与关系等级划分
  tone/             — 人设与语气管理：维持核心人设不变，动态切换语气滤镜
  reflection/       — 反思学习：捕捉用户修正行为，持续微调本地 Skill 参数
"""
