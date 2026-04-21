# tests/ — 单元测试包
# =====================================================
# 覆盖范围：core / brain / probe / ui 各层核心逻辑
#
# 运行方式：
#   pytest                    # 运行全部测试
#   pytest tests/test_skill_distiller.py  # 运行指定模块
#   pytest -v --tb=short      # 详细输出
#
# 测试文件说明：
#   test_skill_distiller.py  — 灵魂蒸馏器：解析、提取、构建 skill 文件
#   test_identity_mapping.py — 联系人分类器与关系人建模
#   test_api_hub.py          — API 路由、适配器、配置管理
#   test_probe.py            — 屏幕探针：只读接口与事件触发（mock 实现）
