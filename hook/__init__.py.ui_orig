"""
ui — 渲染层 (Render Layer)

负责所有与用户直接交互的界面逻辑，包括侧边栏主面板、
幽灵文本（Ghost Text）渲染、Tab 键采纳交互以及设置页面。

子模块：
  sidebar/       — 极客风格侧边栏主面板
    main_panel   : 挂载于微信窗口侧边的分栏容器
    ghost_text   : 幽灵文本渲染器（浅灰色补全提示 + Tab 采纳）
  settings/      — 用户配置界面
    api_config_panel  : BYOK API Key 与模型路由配置面板
    tone_selector     : 语气档位选择器（专业 / 亲和 / 极简）
  tab_handler    — 全局 Tab 键事件监听与采纳逻辑

设计原则：
  - 只读不写：UI 层不修改微信任何控件或内存
  - 非侵入式：作为独立浮层或侧边栏叠加，不影响微信正常使用
  - 极客风格：深色主题、等宽字体、低调的灰色幽灵文本
"""
