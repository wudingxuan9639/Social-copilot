# 2.5 亲密关系与商务社交场景适配 (Scenario Logic)
#
# 职责：
#   - detector        : 根据联系人标签自动识别当前会话场景
#   - prompt_templates: 针对不同场景的 Prompt 模板库
#
# 场景类型：
#   BUSINESS  — 商务场景：专业术语、行动项补全、逻辑严密性优先
#   INTIMATE  — 亲密场景：共情表达、幽默联想、生活化语气优先
#
# 数据流：
#   ContactClassifier.tier
#       └─> ScenarioDetector.detect(contact_id)
#               └─> ScenarioType (BUSINESS / INTIMATE)
#                       └─> PromptTemplate.load(scenario)
#                               └─> brain/api_hub/router.py
