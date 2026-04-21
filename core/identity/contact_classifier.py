# =============================================================================
# core/identity/contact_classifier.py
# 联系人分类器 (Contact Classifier)
# -----------------------------------------------------------------------------
# 职责：
#   根据 myself.skill 中的语料特征，对微信联系人进行自动分级与标注。
#
# 分类维度：
#   - 备注名关键词（如"老板"、"同学"、"老婆"）
#   - 聊天频率与最近活跃时间
#   - 共同高频关键词（如"需求"、"方案" → 商务；"吃饭"、"宝贝" → 亲密）
#
# 输出标签：
#   ContactTier.BUSINESS    —— 商务/职业关系
#   ContactTier.INTIMATE    —— 亲密/家庭关系
#   ContactTier.SOCIAL      —— 泛社交/普通朋友
#   ContactTier.UNKNOWN     —— 待分类
#
# 上游依赖：
#   core/skill_distiller/skill_builder.py  →  读取 myself.skill
#
# 下游调用：
#   brain/scenario/detector.py             →  触发对应 Prompt 策略
#   brain/api_hub/router.py                →  触发对应模型路由
# =============================================================================


class ContactTier:
    """联系人等级枚举（占位，待实现）"""
    BUSINESS = "business"
    INTIMATE = "intimate"
    SOCIAL   = "social"
    UNKNOWN  = "unknown"


class ContactClassifier:
    """
    联系人分类器主类（骨架占位）

    TODO:
        - __init__: 加载 myself.skill，初始化关键词权重表
        - classify(contact_id) -> ContactTier: 对单个联系人打标签
        - batch_classify(contact_list) -> dict: 批量分类并缓存到 data/contacts/
        - update_tier(contact_id, feedback): 接收 Reflection Loop 的修正信号
    """
    pass
