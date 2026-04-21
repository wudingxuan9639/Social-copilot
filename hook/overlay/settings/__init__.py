# ui/settings — 设置面板包 (Settings Panel)
#
# 职责：
#   提供用户配置界面，包括 API Key 填写、模型路由规则设置、语气档位选择等。
#
# 子模块：
#   api_config_panel.py  — BYOK API 配置面板：填入 Key、Base URL、模型名称
#   tone_selector.py     — 语气档位选择器：PROFESSIONAL / WARM / MINIMAL 切换
#
# 设计原则：
#   - 所有用户输入的敏感信息（API Key）仅写入本地 config/secrets.yaml，不做任何网络上报
#   - 设置变更后即时生效，无需重启应用
#   - 面板风格与侧边栏主界面保持一致（极客风格，深色主题）
