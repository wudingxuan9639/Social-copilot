# brain/scenario/detector.py
# =============================================================================
# 场景识别器 (Scenario Detector)
# 对应 PRD 2.5 — 亲密关系与商务社交场景适配 (Scenario Logic)
# =============================================================================
#
# 模块职责：
#   根据当前对话的联系人标签、消息内容及上下文，自动判断当前会话
#   属于「商务场景」还是「亲密场景」，并向 api_hub/router.py 推送
#   对应的 Prompt 模板与模型路由策略。
#
# 两大核心场景定义：
#   ┌─────────────┬──────────────────────────────────────────────────┐
#   │ 场景类型     │ 特征信号                                          │
#   ├─────────────┼──────────────────────────────────────────────────┤
#   │ BUSINESS    │ 联系人 tier=BUSINESS，关键词含「方案/需求/对接」    │
#   │ INTIMATE    │ 联系人 tier=INTIMATE，关键词含「吃饭/宝贝/婚礼」    │
#   └─────────────┴──────────────────────────────────────────────────┘
#
# 检测输入来源（多信号融合）：
#   1. core/identity/contact_classifier.py  —— 联系人 tier 标签
#   2. probe 层捕获的当前对话上下文          —— 实时消息关键词
#   3. brain/rag/retriever.py 返回的文档片段 —— 知识库命中主题
#
# 输出：
#   ScenarioContext 对象，包含：
#     - scenario_type : Literal["business", "intimate", "mixed"]
#     - confidence    : float (0.0 ~ 1.0)
#     - active_template_path : str  (对应的 prompt_templates/ 文件路径)
#     - suggested_model_key  : str  (建议调用的模型标识符)
#
# 依赖：
#   core/identity/contact_classifier.py
#   brain/scenario/prompt_templates/business.md
#   brain/scenario/prompt_templates/intimate.md
#   brain/api_hub/router.py  （下游消费者）
#
# 待实现类与函数：
#   class ScenarioContext
#       scenario_type     : str
#       confidence        : float
#       active_template_path : str
#       suggested_model_key  : str
#
#   class ScenarioDetector
#       def detect(contact_id: str, message_snippet: str) -> ScenarioContext
#           多信号融合打分，返回场景上下文
#       def load_templates() -> dict[str, str]
#           预加载 prompt_templates/ 目录下的所有模板文件
#       def override(contact_id: str, scenario: str) -> None
#           允许用户手动覆盖自动判断结果（UI 设置项）
#
# TODO:
#   [ ] 定义关键词权重词典（business_keywords / intimate_keywords）
#   [ ] 实现多信号加权打分算法
#   [ ] 支持「混合场景」（mixed）的降级处理策略
#   [ ] 添加场景判断日志，供 Reflection Loop 后续分析
# =============================================================================
