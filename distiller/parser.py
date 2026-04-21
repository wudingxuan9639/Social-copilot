# core/skill_distiller/parser.py
# ─────────────────────────────────────────────────────────────────────────────
# 模块职责：微信聊天记录解析器
# ─────────────────────────────────────────────────────────────────────────────
# 输入：本地微信数据库路径 或 导出的聊天记录文本/CSV 文件
# 输出：结构化的对话语料列表，供 feature_extractor.py 使用
#
# 主要职责：
#   1. 定位并读取本地微信聊天数据库（macOS: ~/Library/Containers/com.tencent.xinWeChat）
#   2. 解析消息类型（文本 / 图片 / 语音 / 系统消息），过滤非文本内容
#   3. 按联系人分组，保留时间戳、发送方向（sent/received）
#   4. 输出标准化的 Message 数据模型列表
#
# 待实现的主要函数/类：
#   - class WeChatParser          — 解析器主类
#   - WeChatParser.locate_db()    — 自动定位本地数据库路径
#   - WeChatParser.load()         — 加载并解密数据库（只读模式）
#   - WeChatParser.parse_contact(contact_id) — 解析单个联系人的对话记录
#   - WeChatParser.export_corpus() — 导出全量语料供蒸馏使用
#
# 数据模型（待定义）：
#   Message:
#     - id: str
#     - contact_id: str
#     - direction: Literal["sent", "received"]
#     - content: str
#     - timestamp: datetime
#
# 注意事项：
#   - 严格只读，不得写入或修改任何微信数据库文件
#   - 需要处理微信数据库的 WCDB 加密格式（需用户提供解密密钥或授权）
#   - 大型数据库应支持分批次流式读取，避免内存溢出
# ─────────────────────────────────────────────────────────────────────────────
