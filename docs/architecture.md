# 系统架构文档 · Architecture Overview

> Social Copilot V5.0 · 底座与模型分离架构

---

## 一、架构哲学

本系统遵循三条核心设计原则：

| 原则 | 说明 |
|------|------|
| **解耦** | 本地底座（Skill）与云端大脑（Brain）完全分离，互不依赖 |
| **只读** | 感知层（Probe）仅读取屏幕内容，绝不修改任何目标应用 |
| **自进化** | Reflection Loop 持续收集用户反馈，本地 Skill 随时间自我微调 |

---

## 二、系统分层总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                         用户（微信界面）                              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ 只读旁观（Probe）
┌──────────────────────────────▼──────────────────────────────────────┐
│                       感知层 (Probe Layer)                           │
│   macOS: Accessibility API / Vision OCR                             │
│   Windows: UIAutomation                                             │
│   输出：ConversationContext { contact, messages, input_text }        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐
│  本地底座层      │  │  云端大脑层      │  │     渲染层 (UI Layer)    │
│  (Core Layer)   │  │  (Brain Layer)  │  │                         │
│                 │  │                 │  │  侧边栏主面板             │
│  skill_distiller│  │  api_hub/       │  │  幽灵文本 Ghost Text     │
│  identity/      │◄─►  scenario/      │  │  语气选择器              │
│  tone/          │  │  rag/           │  │  API 配置面板            │
│  reflection/    │  │                 │  │  Tab 键采纳              │
└─────────────────┘  └─────────────────┘  └─────────────────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    本地数据目录       │
                    │  data/skill/        │
                    │  data/feedback/     │
                    │  data/contacts/     │
                    └─────────────────────┘
```

---

## 三、各层详细说明

### 3.1 感知层 (Probe Layer)

**职责**：以只读方式从微信窗口获取实时数据，是整个系统的数据入口。

**输入**：微信当前窗口状态（不修改、不侵入）

**输出**：
- `input_text`：用户当前正在输入的半句话
- `conversation_context`：最近 N 条对话消息
- `active_contact`：当前正在聊天的联系人信息

**平台双轨实现**：

```
ProbeFactory.create()
    ├── sys.platform == "darwin"
    │       ├── 首选：AccessibilityProbe（AXUIElement API）
    │       └── 备选：VisionOCRProbe（Vision Framework）
    └── sys.platform == "win32"
            └── 首选：UIAutomationProbe（UIAutomation API）
```

**关键约束**：
- 捕获频率防抖（debounce 300ms）
- 数据仅在内存中流转，不持久化
- 任何读取失败均静默降级，不影响用户正常使用微信

---

### 3.2 本地底座层 (Core Layer)

这是系统的"灵魂"所在，所有运算完全在本地完成，不依赖网络。

#### 3.2.1 Skill Distiller（灵魂蒸馏器）

```
微信数据库（只读）
    └─> WeChatParser.parse()
            └─> FeatureExtractor.extract()
                    ├── 高频词 / 短语
                    ├── 句式偏好
                    ├── 情绪色彩分布
                    ├── 专业术语命中
                    └── Emoji / 称谓习惯
                            └─> SkillBuilder.build()
                                    └─> Encryptor.encrypt()
                                            └─> data/skill/myself.skill
```

`myself.skill` 是整个底座层的核心资产，其他所有模块均以此为数据源。

#### 3.2.2 Identity Mapping（身份建模）

```
myself.skill
    └─> ContactClassifier.classify(contact_id)
            ├── 分析备注名关键词
            ├── 聊天频率指数
            └── 共同高频关键词
                    └─> ContactTier: BUSINESS | INTIMATE | SOCIAL | UNKNOWN
                            └─> RelationshipProfile（联系人画像）
```

#### 3.2.3 Tone Mask（人设与语气）

```
myself.skill
    └─> PersonaManager.load()       → PersonaProfile（身份底色，永久稳定）
            └─> ToneFilter.apply()  → 应用语气档位（PROFESSIONAL | WARM | MINIMAL）
                    └─> 风格化后的建议文本 → 渲染层
```

#### 3.2.4 Reflection Loop（反思学习）

```
用户采纳/修改行为
    └─> DiffTracker.compare(ai_draft, user_final)
            └─> SemanticDiff { delta_vector, context }
                    └─> data/feedback/{date}.jsonl
                            └─> SkillUpdater.apply_feedback()
                                    └─> myself.skill（参数微调，版本快照）
```

---

### 3.3 云端大脑层 (Brain Layer)

无状态层，仅负责将结构化上下文转化为 AI 生成结果，不持久化任何数据。

#### 3.3.1 Scenario Logic（场景识别）

```
ContactTier + 消息关键词 + RAG 命中主题
    └─> ScenarioDetector.detect()
            └─> ScenarioContext {
                    scenario_type: "business" | "intimate",
                    active_template: prompt_templates/business.md,
                    suggested_model: "deepseek-chat"
                }
```

#### 3.3.2 RAG 知识库（上下文增强）

```
当前对话文本
    └─> RAGRetriever.query(text, scenario_tag)
            └─> ChromaDB（本地向量索引）
                    └─> TopK 相关知识片段
                            └─> 注入 Prompt 的 [CONTEXT] 区域
```

知识库文档由用户自己维护（`brain/rag/knowledge_base/`），系统负责自动索引。

#### 3.3.3 API Hub（多模型路由）

```
ScenarioContext + PersonaProfile + RAGChunks
    └─> PromptBuilder.assemble()       → 完整 Prompt
            └─> APIRouter.route()
                    ├── BUSINESS → DeepSeekAdapter → deepseek-chat
                    ├── INTIMATE → DoubaoAdapter   → doubao-pro-32k
                    └── DEFAULT  → OpenAIAdapter   → user-configured
                            └─> GenerationResult { text, token_usage, latency }
```

**BYOK 原则**：API Key 由用户自持，存于本地 `config/secrets.yaml`（.gitignore 保护），软件仅在内存中短暂使用，不做任何上报。

---

### 3.4 渲染层 (UI Layer)

**职责**：将 AI 建议呈现给用户，同时接收用户的采纳/拒绝决策。

#### Ghost Text 生命周期

```
用户输入（partial_input）
    └─> GhostTextRenderer.on_input_change()    [防抖 300ms]
            └─> brain 层异步生成
                    └─> GhostTextRenderer.start_stream()
                            └─> 浅灰色渲染（#AAAAAA, italic）
                                    ├── Tab  → accept()  → 复制到剪贴板 → ACCEPTED
                                    ├── Esc  → dismiss() → DISMISSED
                                    └── 继续输入 → 隐式拒绝 → 触发新一轮生成
```

#### 侧边栏组件树

```
SocialCopilotSidebar (QWidget, 无边框置顶)
    ├── StatusBar          联系人名称 + 场景标签 + 模型指示灯
    ├── SuggestionCards    2-3 条 AI 候选回复卡片（可点击采纳）
    ├── GhostTextPreview   实时幽灵文本预览区
    ├── ToneSelector       专业 · 亲和 · 极简 三档切换
    └── ActionBar          刷新建议 / 打开设置 / 反馈
```

---

## 四、完整数据流（端到端）

```
① 用户在微信输入框输入："我觉得这个方案"
         │
         ▼
② Probe 捕获 input_text = "我觉得这个方案"
   同时读取 active_contact = "张总"
         │
         ▼
③ ContactClassifier 识别 tier = BUSINESS
         │
         ▼
④ ScenarioDetector 输出 scenario = "business"
   挂载 prompt_templates/business.md
         │
         ▼
⑤ RAGRetriever 检索 knowledge_base/business/
   召回 "主包对接方案.md" 相关片段
         │
         ▼
⑥ PersonaManager 提取用户身份底色
   ToneFilter 应用 PROFESSIONAL 档位
         │
         ▼
⑦ PromptBuilder 组装完整 Prompt
   APIRouter 路由至 DeepSeekAdapter
         │
         ▼
⑧ DeepSeek API 返回流式补全内容：
   "...可行，建议本周四安排评审，确认接口规范后再推进排期。"
         │
         ▼
⑨ GhostTextRenderer 渲染浅灰色预览
         │
     Tab 按下
         │
         ▼
⑩ TabHandler.accept()
   文本复制到剪贴板
   DiffTracker 记录采纳事件
   SkillUpdater 微调 myself.skill
```

---

## 五、模块依赖关系图

```
probe/
  └─> core/identity/          (contact 分类)
  └─> brain/scenario/         (场景识别触发)
  └─> ui/sidebar/ghost_text   (输入变更通知)

core/skill_distiller/
  └─> core/identity/          (提供联系人画像原始数据)
  └─> core/tone/              (提供人设底色)
  └─> core/reflection/        (接收 Skill 更新指令)

brain/scenario/
  └─> core/identity/          (读取 ContactTier)
  └─> brain/rag/              (触发知识库检索)
  └─> brain/api_hub/          (传递 ScenarioContext)

brain/api_hub/
  └─> brain/scenario/         (获取 Prompt 模板)
  └─> brain/rag/              (获取 RAG 片段)
  └─> core/tone/              (获取人设 + 语气)
  └─> ui/sidebar/ghost_text   (推送生成结果)

ui/tab_handler
  └─> ui/sidebar/ghost_text   (控制显示/清除)
  └─> core/reflection/        (发送采纳/拒绝事件)
  └─> brain/api_hub/          (触发新一轮生成)
```

---

## 六、数据存储一览

| 存储位置 | 内容 | 加密 | 上传云端 |
|----------|------|------|----------|
| `data/skill/myself.skill` | 用户高频特征、人设底色、联系人画像 | ✅ AES-256 | ❌ 绝不 |
| `data/feedback/*.jsonl` | Reflection Loop 差异记录 | ❌ 明文 | ❌ 绝不 |
| `data/contacts/*.json` | 联系人分类缓存 | ❌ 明文 | ❌ 绝不 |
| `config/models.yaml` | API 路由规则（不含密钥） | ❌ 明文 | ⚠️ 注意 |
| `config/secrets.yaml` | API Key（.gitignore 保护） | ❌ 明文 | ❌ 绝不 |
| `brain/rag/knowledge_base/` | 用户自定义知识库 Markdown | ❌ 明文 | ❌ 绝不 |

---

## 七、开发阶段与模块映射

| 阶段 | 目标 | 涉及模块 | 交付物 |
|------|------|----------|--------|
| **Phase 1** | 本地 Skill 蒸馏器 | `core/skill_distiller/` | `myself.skill` 文件生成脚本 |
| **Phase 2** | 非侵入式输入监听 + Ghost Text | `probe/` + `ui/sidebar/` | 能读取输入框并渲染浅灰色提示 |
| **Phase 3** | 多模型路由 + RAG 整合 | `brain/api_hub/` + `brain/rag/` | 完整端到端补全流程可用 |
| **Phase 4** | Reflection Loop | `core/reflection/` | Skill 随使用自动微调 |

---

## 八、关键技术选型

| 技术域 | 选型 | 理由 |
|--------|------|------|
| GUI 框架 | PyQt6 | 跨平台、成熟、支持无边框悬浮窗 |
| macOS 探针 | pyobjc + AXUIElement | 官方 API，无需注入，合规 |
| Windows 探针 | uiautomation | 无需注入，纯读取，合规 |
| AI 调用 | openai SDK (>=1.0) | 兼容所有 OpenAI 协议的模型 |
| 向量数据库 | ChromaDB | 纯本地，零部署，Python 原生 |
| Embedding | sentence-transformers | 本地推理，数据不出设备 |
| 中文分词 | jieba | 轻量、成熟、离线可用 |
| 加密 | cryptography (AES-256-GCM) | 工业标准，Python 原生绑定 |
| 异步运行时 | asyncio + httpx | 全链路异步，不阻塞 UI 线程 |

---

*Architecture Version: 1.0 · 对应 PRD V5.0 · 架构原则：解耦、只读、自进化*