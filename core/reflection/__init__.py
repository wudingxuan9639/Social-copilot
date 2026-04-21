"""
core.reflection — 协作修正与反思学习 (Reflection Loop)

职责：
  - 捕捉用户拒绝 AI 建议后手动修改的终稿内容
  - 计算终稿与 AI 草稿之间的语义差异（偏差向量）
  - 将偏差反馈写回本地 Skill，逐步微调生成参数

子模块：
  diff_tracker   : 终稿 vs 草稿的 diff 捕捉与语义比对
  skill_updater  : 基于偏差反馈更新 myself.skill 中的权重参数
"""
