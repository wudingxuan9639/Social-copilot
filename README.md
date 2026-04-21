# 微信社交副驾 · Social Copilot

> 底座软件负责"灵魂提取"（Skill），外部 API 负责"逻辑生成"（Brain），用户通过 Tab 键完成"社交增强"。

非侵入式侧边栏补全工具 —— **只读不写，人工决策**。

---

## 产品哲学

本系统采用"底座与模型分离"的设计，将**本地私有数据处理**与**云端生成能力**彻底解耦：

| 层级 | 职责 | 关键产物 |
|------|------|----------|
| **本地底座层**（Skill） | 灵魂提取：扫描微信记录，提炼用户表达特征 | `myself.skill` |
| **云端大脑层**（Brain） | 逻辑生成：BYOK 接入任意兼容 OpenAI 协议的模型 | API 路由 + Prompt |
| **感知渲染层**（Probe + UI） | 屏幕只读 + 幽灵文本补全 | Tab 键采纳 |

---

## 项目结构

```
social-copilot/
│
├── core/                        # 本地底座层 —— 灵魂提取
│   ├── skill_distiller/         # [阶段1] 本地 Skill 蒸馏器
│   ├── identity/                # [2.1] 角色信息分类 (Identity Mapping)
│   ├── tone/                    # [2.2] 人设一致性与语气切换 (Tone Mask)
│   └── reflection/              # [2.4] 协作修正与反思学习 (Reflection Loop)
│
├── brain/                       # 云端大脑层 —— 逻辑生成
│   ├── api_hub/                 # [2.3] 灵活 API 接入 (Flexible Hub / BYOK)
│   │   └── adapters/            # 各模型适配器（DeepSeek / 豆包 / 通义）
│   ├── scenario/                # [2.5] 商务 / 亲密场景适配 (Scenario Logic)
│   │   └── prompt_templates/    # Prompt 模板库
│   └── rag/                     # RAG 本地知识库挂载
│       └── knowledge_base/      # 用户自定义 Markdown 资料
│
├── probe/                       # 感知层 —— 屏幕只读探针
│   ├── macos/                   # Accessibility API + Vision OCR
│   └── windows/                 # UIAutomation
│
├── ui/                          # 渲染层 —— 侧边栏界面
│   ├── sidebar/                 # [2.6] 幽灵文本 (Ghost Text)
│   └── settings/                # API 配置 + 语气选择器
│
├── data/                        # 本地加密数据目录（不上传）
│   ├── skill/                   # myself.skill 存储
│   ├── feedback/                # Reflection Loop 反馈记录
│   └── contacts/                # 联系人分类缓存
│
├── config/                      # 配置文件
├── tests/                       # 单元测试
└── docs/                        # 开发文档
```

---

## 六大核心功能

### 2.1 Identity Mapping · 角色信息分类
通过备注名、聊天频率、共同关键词自动划分联系人等级，确保 AI 建议精准对应"对方是谁"。

### 2.2 Tone Mask · 人设与语气切换
身份底色（专业背景、核心人设）保持稳定，提供**专业 / 亲和 / 极简**三种语气滤镜，一键切换。

### 2.3 Flexible Hub · BYOK 接入
支持任何兼容 OpenAI 协议的 API。商业场景可接 DeepSeek，亲密场景可接豆包，按需分配。

### 2.4 Reflection Loop · 反思学习
捕捉用户拒绝 AI 建议后的手动修改，记录终稿与草稿的语义差异，持续微调本地 Skill 参数。

### 2.5 Scenario Logic · 场景适配
- **商务场景**：专业术语、行动项补全、逻辑严密性
- **亲密场景**：共情表达、幽默联想、生活化语气

### 2.6 Ghost Text & Tab · 幽灵补全
用户输入半句话后，AI 预测内容以浅灰色显示；按下 `Tab` 即采纳，降低 I 人社交焦虑。

---

## 开发阶段路线图

| 阶段 | 目标 | 核心模块 |
|------|------|----------|
| **Phase 1** | 本地 Skill 蒸馏器 | `core/skill_distiller/` |
| **Phase 2** | 非侵入式输入监听 + 幽灵文本渲染 | `probe/` + `ui/sidebar/` |
| **Phase 3** | 多模型路由 + RAG 整合 | `brain/api_hub/` + `brain/rag/` |

---

## 隐私原则

- **只读不写**：不修改微信内存，不侵入协议层
- **本地加密**：`myself.skill` 及所有派生数据仅存于本机
- **BYOK**：API Key 由用户自持，软件不经手任何密钥上报

---

## 快速开始

> 详见 `docs/` 目录下各阶段开发指南。

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化 Skill 蒸馏（Phase 1）
python -m core.skill_distiller

# 3. 配置你的 API（BYOK）
cp config/models.yaml.example config/models.yaml
# 编辑 models.yaml，填入你的 API Key 与 Base URL

# 4. 启动主程序
python main.py
```

---

*PRD Version: V5.0 · 架构设计原则：解耦、只读、自进化*