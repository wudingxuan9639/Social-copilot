"""
brain — 云端大脑层 (Cloud Brain / BYOK)

负责所有与外部 AI 模型的交互逻辑。本层不处理任何私有数据，
仅接收来自 core 层的结构化上下文，通过用户自持的 API Key 调用外部模型。

子模块：
  api_hub/     — 灵活 API 接入 (Flexible Hub)：BYOK 路由调度，支持任意 OpenAI 兼容协议
  scenario/    — 场景适配逻辑 (Scenario Logic)：商务 / 亲密场景识别与 Prompt 策略切换
  rag/         — 本地 RAG 知识库：挂载用户自定义 Markdown 资料，增强上下文精准度

设计原则：
  - 无状态：brain 层不持久化任何数据，所有状态由 core 层管理
  - 可替换：任意子模块（api_hub / scenario）均可独立替换，不影响其他层
  - 无密钥托管：API Key 仅在内存中短暂存在，不写入磁盘
"""
