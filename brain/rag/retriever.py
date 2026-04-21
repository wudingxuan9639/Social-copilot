# retriever.py
# ─────────────────────────────────────────────────────────────────────────────
# 模块职责：RAG 本地知识库检索器 (Retrieval-Augmented Generation Retriever)
# ─────────────────────────────────────────────────────────────────────────────
#
# 核心思路：
#   将用户存放在 brain/rag/knowledge_base/ 目录下的 Markdown 文件
#   向量化并索引到本地向量数据库（ChromaDB），在生成 AI 回复前，
#   根据当前对话上下文检索最相关的知识片段，拼入 Prompt，
#   从而让 AI "知道"用户的专属背景信息。
#
# 数据流：
#   knowledge_base/*.md
#       └─> Chunker（文本分块）
#               └─> Embedder（本地向量化）
#                       └─> ChromaDB（持久化向量存储）
#                               └─> Retriever.query(context) -> list[Chunk]
#                                       └─> brain/api_hub/router.py（拼入 Prompt）
#
# 知识库目录约定（brain/rag/knowledge_base/）：
#   - business/     — 商务场景相关资料（项目背景、技术术语、合作方信息）
#   - intimate/     — 亲密场景相关资料（家庭事项、宠物、婚礼进度等）
#   - shared/       — 通用背景资料（自我介绍、技能清单等）
#
# 主要类与函数（待实现）：
#
#   class KnowledgeChunk
#       ├── id          : str          — 文档块唯一 ID
#       ├── source_file : str          — 来源 Markdown 文件路径
#       ├── content     : str          — 原始文本内容
#       ├── embedding   : list[float]  — 向量表示（存于 ChromaDB）
#       └── metadata    : dict         — 标签（scenario_tag、contact_tier 等）
#
#   class RAGRetriever
#       ├── __init__(db_path, embedding_model)
#       │       — 初始化向量数据库连接与 Embedding 模型（本地运行，无需联网）
#       │
#       ├── build_index(knowledge_dir: str) -> None
#       │       — 扫描 knowledge_base/ 下的所有 .md 文件
#       │       — 按段落/标题分块，生成向量并写入 ChromaDB
#       │
#       ├── query(context: str, scenario_tag: str, top_k: int) -> list[KnowledgeChunk]
#       │       — 将当前对话上下文向量化，在 ChromaDB 中做近似最近邻检索
#       │       — 支持按 scenario_tag 过滤（business / intimate / shared）
#       │       — 返回 top_k 个最相关的知识块
#       │
#       ├── format_for_prompt(chunks: list[KnowledgeChunk]) -> str
#       │       — 将检索结果格式化为可直接拼入 Prompt 的 Markdown 字符串
#       │
#       └── refresh_index() -> None
#               — 监听 knowledge_base/ 目录变更，增量更新索引
#               — 可手动触发或在应用启动时自动检查
#
# 配置项（来自 config/app_config.yaml）：
#   rag.embedding_model     : 本地 Embedding 模型名称（默认：BAAI/bge-small-zh-v1.5）
#   rag.db_path             : ChromaDB 持久化路径（默认：data/rag_index/）
#   rag.chunk_size          : 文本分块大小（默认：512 tokens）
#   rag.chunk_overlap       : 相邻块重叠 token 数（默认：64）
#   rag.top_k               : 默认检索返回块数（默认：3）
#
# 依赖：
#   - chromadb                  — 本地向量数据库
#   - sentence-transformers     — 本地 Embedding 模型推理
#   - brain/scenario/detector.py — 获取当前 scenario_tag，用于过滤检索范围
#
# 隐私原则：
#   - 所有 Embedding 推理在本地完成，不向外部发送用户知识库内容
#   - ChromaDB 索引文件存于 data/ 目录（已在 .gitignore 中排除）
# ─────────────────────────────────────────────────────────────────────────────
