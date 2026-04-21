"""
brain.rag — 本地 RAG 知识库挂载模块 (Retrieval-Augmented Generation)

职责：
  - 管理用户自定义的本地 Markdown 知识资料（存放于 knowledge_base/ 目录）
  - 对文档进行向量化索引，支持语义检索
  - 在 AI 生成补全建议前，自动检索并注入相关上下文片段

子模块：
  retriever        : 语义检索器，根据当前对话内容召回最相关的知识片段
  knowledge_base/  : 用户自定义 Markdown 资料目录（本地，不上传）

典型数据流：
  当前对话文本
      └─> retriever.query(text, contact_tier)
              └─> 向量数据库（本地 ChromaDB）
                      └─> TopK 相关文档片段
                              └─> 注入 brain/api_hub/router.py 的 Prompt 上下文

设计原则：
  - 所有向量索引与文档数据仅存储于本地，绝不上传至云端
  - 支持增量索引：knowledge_base/ 目录内容更新后自动重建相关索引
  - 联系人场景标签（business / intimate）可作为检索过滤条件
"""
