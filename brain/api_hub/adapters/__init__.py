# brain/api_hub/adapters — 多模型适配器包
# =============================================
# 每个适配器封装一个具体 AI 服务商的 API 调用细节，
# 对外统一暴露相同的接口契约，由 router.py 按需调度。
#
# 当前适配器列表：
#   openai_adapter.py    — 标准 OpenAI 协议（兼容 GPT-4 / 通义千问等）
#   deepseek_adapter.py  — DeepSeek 专属适配（商务强逻辑场景推荐）
#   doubao_adapter.py    — 豆包 / 火山引擎适配（亲密拟人场景推荐）
#
# 扩展方式：
#   新增适配器时，继承 BaseAdapter 并实现 complete() 方法，
#   然后在此处注册到 ADAPTER_REGISTRY 即可。
