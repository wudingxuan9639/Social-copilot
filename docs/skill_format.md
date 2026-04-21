# myself.skill 文件格式规范

> 版本：v1.0  
> 路径：`data/skill/myself.skill`  
> 加密：AES-256-GCM（设备指纹派生密钥，密钥不离本机）

---

## 概述

`myself.skill` 是整个 Social Copilot 系统的"灵魂文件"，由 `core/skill_distiller/` 模块从本地微信聊天记录中提炼生成。它是一个经过本地加密存储的 JSON 文档，记录了用户的语言特征、身份背景、联系人画像等私有数据。

**所有 AI 生成逻辑的个性化依据均来自此文件。**

---

## 顶层结构

```json
{
  "version": "1.0",
  "created_at": "2025-01-01T00:00:00+08:00",
  "updated_at": "2025-07-01T12:00:00+08:00",
  "distill_stats": { ... },
  "identity": { ... },
  "language_profile": { ... },
  "contacts": [ ... ],
  "reflection_log": [ ... ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `version` | string | Skill 文件格式版本号，用于向后兼容迁移 |
| `created_at` | ISO 8601 | 首次生成时间 |
| `updated_at` | ISO 8601 | 最后更新时间（每次蒸馏或 Reflection 后刷新） |
| `distill_stats` | object | 本次蒸馏的统计元信息 |
| `identity` | object | 用户身份底色（核心人设） |
| `language_profile` | object | 语言特征画像（高频词、句式、情绪分布等） |
| `contacts` | array | 联系人分类画像列表 |
| `reflection_log` | array | Reflection Loop 的历史修正记录摘要 |

---

## 1. `distill_stats` — 蒸馏统计元信息

```json
"distill_stats": {
  "total_messages_scanned": 42680,
  "date_range": {
    "start": "2022-03-01",
    "end": "2025-06-30"
  },
  "contacts_analyzed": 87,
  "corpus_size_chars": 1250000,
  "distill_duration_seconds": 34.7
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_messages_scanned` | int | 参与蒸馏的消息总条数 |
| `date_range.start` | string | 语料起始日期 |
| `date_range.end` | string | 语料截止日期 |
| `contacts_analyzed` | int | 参与分析的联系人数量 |
| `corpus_size_chars` | int | 语料总字符数 |
| `distill_duration_seconds` | float | 本次蒸馏耗时（秒） |

---

## 2. `identity` — 用户身份底色

此部分对应 PRD 2.2（Tone Mask）中的"身份底色不变"原则。
无论回复哪位联系人，`identity` 的内容都会稳定地注入 System Prompt。

```json
"identity": {
  "inferred_profession": "前端工程师",
  "inferred_life_stage": "准新郎",
  "core_tags": ["技术宅", "独立思考", "内向", "幽默"],
  "expertise_keywords": ["React", "TypeScript", "架构设计", "性能优化"],
  "self_description": "资深前端开发者，擅长工程化建设，偶尔用梗表达观点，不喜欢废话连篇。",
  "confidence_scores": {
    "inferred_profession": 0.92,
    "inferred_life_stage": 0.85
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `inferred_profession` | string | 从语料中推断的职业（含置信度） |
| `inferred_life_stage` | string | 当前人生阶段标签（如"准新郎"、"新手爸妈"） |
| `core_tags` | string[] | 性格/风格标签，注入 Prompt 用于人设约束 |
| `expertise_keywords` | string[] | 专业领域高频词，用于商务场景 Prompt 增强 |
| `self_description` | string | 综合推断出的一句话人设描述，直接用于 System Prompt |
| `confidence_scores` | object | 各推断字段的置信度（0~1），低于 0.6 时提示用户手动确认 |

> **注意**：`identity` 中的内容由蒸馏器自动推断，用户可在设置面板中手动覆盖和修正任何字段。

---

## 3. `language_profile` — 语言特征画像

此部分是"灵魂蒸馏"的核心产物，记录了用户从数万条消息中提炼出的语言习惯。

```json
"language_profile": {
  "top_phrases": [
    { "text": "行，我看看", "frequency": 312, "context_tags": ["response", "casual"] },
    { "text": "没问题", "frequency": 287, "context_tags": ["agreement", "business"] },
    { "text": "稍等一下", "frequency": 201, "context_tags": ["delay", "casual"] },
    { "text": "好的好的", "frequency": 198, "context_tags": ["agreement", "casual"] },
    { "text": "这个可以", "frequency": 176, "context_tags": ["approval", "business"] }
  ],
  "sentence_patterns": {
    "question_ratio": 0.18,
    "statement_ratio": 0.67,
    "exclamation_ratio": 0.08,
    "ellipsis_usage": 0.12,
    "avg_sentence_length": 14.3
  },
  "tone_distribution": {
    "positive": 0.52,
    "neutral": 0.38,
    "negative": 0.10
  },
  "emoji_profile": {
    "usage_frequency": 0.23,
    "top_emojis": ["😂", "👍", "🤔", "😅", "🙏"],
    "style": "sparingly"
  },
  "address_habits": {
    "formal_ratio": 0.31,
    "informal_ratio": 0.69,
    "common_salutations": ["哥", "老师", "朋友", "宝"]
  },
  "humor_index": 0.64,
  "verbosity_index": 0.38
}
```

### 3.1 `top_phrases` — 高频短语

| 字段 | 类型 | 说明 |
|------|------|------|
| `text` | string | 高频短语文本 |
| `frequency` | int | 在语料中出现的绝对次数 |
| `context_tags` | string[] | 出现场景标签（如 `casual`、`business`、`agreement`） |

### 3.2 `sentence_patterns` — 句式偏好

| 字段 | 类型 | 说明 |
|------|------|------|
| `question_ratio` | float | 疑问句占比 |
| `statement_ratio` | float | 陈述句占比 |
| `exclamation_ratio` | float | 感叹句占比 |
| `ellipsis_usage` | float | 省略号/省略表达使用占比 |
| `avg_sentence_length` | float | 平均句子字数 |

### 3.3 `tone_distribution` — 情绪色彩分布

| 字段 | 类型 | 说明 |
|------|------|------|
| `positive` | float | 正向情绪占比（愉快、认同、积极） |
| `neutral` | float | 中性情绪占比（陈述事实、传递信息） |
| `negative` | float | 负向情绪占比（不满、拒绝、消极） |

### 3.4 `emoji_profile` — Emoji 使用画像

| 字段 | 类型 | 说明 |
|------|------|------|
| `usage_frequency` | float | 含 Emoji 的消息占全部消息的比例 |
| `top_emojis` | string[] | 最常用 Emoji 前 5 个（按频次排序） |
| `style` | string | 使用风格：`sparingly`（克制）/ `frequently`（频繁）/ `never` |

### 3.5 `address_habits` — 称谓习惯

| 字段 | 类型 | 说明 |
|------|------|------|
| `formal_ratio` | float | 使用正式称谓（"您"、"老师"）的占比 |
| `informal_ratio` | float | 使用非正式称谓（"哥"、"宝"）的占比 |
| `common_salutations` | string[] | 最常用的称谓词列表 |

### 3.6 其他指数

| 字段 | 类型 | 说明 |
|------|------|------|
| `humor_index` | float | 幽默感指数（0~1，越高代表越常使用幽默/自嘲表达） |
| `verbosity_index` | float | 话痨指数（0~1，越低越简洁，越高越喜欢展开说） |

---

## 4. `contacts` — 联系人分类画像

```json
"contacts": [
  {
    "id": "wxid_abc123",
    "display_name": "张总",
    "alias": "前主管",
    "tier": "business",
    "scenario_tag": "business",
    "chat_frequency_index": 0.87,
    "last_interaction": "2025-06-28",
    "keyword_cloud": ["项目", "方案", "对接", "排期", "需求"],
    "relationship_notes": "前公司主管，现为合作方，沟通风格偏正式",
    "preferred_tone": "professional",
    "rag_tags": ["project_context", "clients"]
  },
  {
    "id": "wxid_def456",
    "display_name": "老婆",
    "alias": null,
    "tier": "intimate",
    "scenario_tag": "intimate",
    "chat_frequency_index": 0.99,
    "last_interaction": "2025-07-01",
    "keyword_cloud": ["婚礼", "猫咪", "吃饭", "周末", "回家"],
    "relationship_notes": "最高优先级联系人，生活场景为主",
    "preferred_tone": "warm",
    "rag_tags": ["family_events", "pets_hobbies"]
  }
]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 微信唯一 ID（脱敏处理） |
| `display_name` | string | 备注名或微信昵称 |
| `alias` | string \| null | 用户自定义的关系描述 |
| `tier` | string | 关系等级：`business` / `intimate` / `social` / `unknown` |
| `scenario_tag` | string | 触发的 Prompt 场景标签 |
| `chat_frequency_index` | float | 聊天活跃度指数（近 30 天，0~1 归一化） |
| `last_interaction` | string | 最近一次对话日期 |
| `keyword_cloud` | string[] | 与该联系人对话中提炼的高频关键词 Top 10 |
| `relationship_notes` | string | 综合推断的关系描述（可手动编辑） |
| `preferred_tone` | string | 建议的语气档位（`professional` / `warm` / `minimal`） |
| `rag_tags` | string[] | 与该联系人匹配的 RAG 知识库标签（用于精准检索） |

---

## 5. `reflection_log` — 反思学习记录摘要

此部分记录 Reflection Loop（PRD 2.4）产生的历史修正摘要，
用于追踪 Skill 参数的演化轨迹。

```json
"reflection_log": [
  {
    "timestamp": "2025-06-30T21:14:05+08:00",
    "contact_id": "wxid_abc123",
    "ai_draft_summary": "建议了较正式的商务回复（约80字）",
    "user_final_summary": "用户删减为约20字的简短确认",
    "delta_type": "verbosity_reduction",
    "delta_score": -0.42,
    "affected_params": ["verbosity_index", "avg_sentence_length"],
    "skill_version_after": "1.0.7"
  }
]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamp` | ISO 8601 | 修正事件发生时间 |
| `contact_id` | string | 对应的联系人 ID |
| `ai_draft_summary` | string | AI 草稿的简要描述（不存储原文，保护隐私） |
| `user_final_summary` | string | 用户终稿的简要描述 |
| `delta_type` | string | 偏差类型（如 `verbosity_reduction` / `tone_shift` / `style_change`） |
| `delta_score` | float | 偏差幅度（-1~1，负值表示用户趋向简洁，正值趋向展开） |
| `affected_params` | string[] | 本次修正影响了哪些 `language_profile` 参数 |
| `skill_version_after` | string | 修正后 Skill 内部版本号（`major.minor.patch`） |

---

## 6. 版本迁移规则

当 `version` 字段发生变化时，`core/skill_distiller/skill_builder.py` 负责执行迁移逻辑：

| 版本变化 | 迁移策略 |
|----------|----------|
| `patch` 升级（如 1.0.x → 1.0.y） | 自动合并，新字段补充默认值 |
| `minor` 升级（如 1.0 → 1.1） | 自动迁移，弃用字段保留为 `_deprecated_` 前缀 |
| `major` 升级（如 1.x → 2.x） | 需用户确认，备份旧文件后重新蒸馏 |

---

## 7. 加密与存储说明

```
data/skill/
├── myself.skill          ← 当前激活的加密 Skill 文件
├── myself.skill.bak      ← 上一版本备份（每次更新前自动创建）
└── skill_versions/       ← 历史版本快照（保留最近 10 个）
    ├── myself.skill.v1.0.5
    └── myself.skill.v1.0.6
```

- **加密算法**：AES-256-GCM
- **密钥来源**：设备硬件指纹（CPU ID + 主板序列号）经 PBKDF2 派生，密钥永不离开本机
- **文件头**：前 16 字节为版本标记 + IV（初始化向量），后续为密文
- **完整性验证**：GCM 认证标签确保文件未被篡改

---

*文档版本：v1.0 · 对应 core/skill_distiller/ 模块 · 最后更新：2025-07*