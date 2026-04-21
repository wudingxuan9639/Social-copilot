# diff_tracker.py
# ─────────────────────────────────────────────────────────────
# 模块职责：协作修正与反思学习 — 差异捕捉器 (Reflection Loop)
# ─────────────────────────────────────────────────────────────
#
# 核心逻辑（待实现）：
#   1. 监听用户"拒绝 AI 建议并手动修改"的行为事件
#   2. 捕捉 AI 草稿（draft）与用户终稿（final）之间的语义差异
#   3. 将差异记录序列化为结构化反馈对象，写入 data/feedback/
#   4. 向 skill_updater 发出 Skill 微调信号
#
# 数据流：
#   ProbeEvent(用户提交终稿)
#       └─> DiffTracker.compare(draft, final)
#               └─> DiffRecord { timestamp, contact_id, draft, final, delta_score }
#                       └─> data/feedback/{date}.jsonl
#                               └─> SkillUpdater.queue(diff_record)
#
# 依赖：
#   - core/reflection/skill_updater.py   （下游消费者）
#   - data/feedback/                     （持久化目录）
#
# TODO:
#   - [ ] 实现基于语义向量的 diff 算法（非字符级 diff）
#   - [ ] 定义 DiffRecord 数据结构
#   - [ ] 实现 JSONL 滚动写入（按日期分片）
#   - [ ] 定义触发阈值：语义距离 > N 才记录，过滤微小改动
