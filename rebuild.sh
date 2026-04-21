#!/usr/bin/env bash
# =============================================================================
# rebuild.sh — Shadow Clone 重构脚本
# 将项目从 social-copilot 架构迁移至 Shadow Clone 极客风格
# =============================================================================
#
# 目录映射：
#   core/skill_distiller/   →  distiller/
#   core/identity/          →  distiller/persona/
#   core/tone/              →  distiller/persona/
#   core/reflection/        →  distiller/reflection/
#   probe/                  →  hook/
#   ui/sidebar/             →  hook/overlay/
#   ui/settings/            →  hook/overlay/settings/
#   ui/tab_handler.py       →  hook/tab_handler.py
#   brain/                  →  brain/ (不变)
#
# 用法：
#   chmod +x rebuild.sh
#   ./rebuild.sh
# =============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log_step() { echo -e "\n${CYAN}${BOLD}🥷 $1${NC}"; }
log_ok()   { echo -e "  ${GREEN}✓${NC}  $1"; }
log_warn() { echo -e "  ${YELLOW}⚠${NC}  $1"; }

echo -e "${BOLD}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║   Shadow Clone  —  影分身重构启动     ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${NC}"

# =============================================================================
# 0. 安全检查
# =============================================================================
log_step "安全检查..."

if [ ! -f "main.py" ] || [ ! -d "core" ] || [ ! -d "probe" ]; then
    echo -e "${RED}✗  当前目录不是 social-copilot 项目根目录，终止。${NC}"
    exit 1
fi

if [ -d "distiller" ] || [ -d "hook" ]; then
    echo -e "${RED}✗  distiller/ 或 hook/ 目录已存在，疑似已执行过重构，终止。${NC}"
    exit 1
fi

log_ok "项目结构校验通过"

# =============================================================================
# 1. 创建新目录结构
# =============================================================================
log_step "创建 Shadow Clone 目录结构..."

mkdir -p distiller/persona
mkdir -p distiller/reflection
mkdir -p hook/macos
mkdir -p hook/windows
mkdir -p hook/overlay/settings

log_ok "distiller/ distiller/persona/ distiller/reflection/"
log_ok "hook/ hook/macos/ hook/windows/ hook/overlay/ hook/overlay/settings/"

# =============================================================================
# 2. 迁移 distiller/（原 core/skill_distiller/）
# =============================================================================
log_step "迁移 core/skill_distiller → distiller/..."

for f in core/skill_distiller/__init__.py \
          core/skill_distiller/parser.py \
          core/skill_distiller/feature_extractor.py \
          core/skill_distiller/skill_builder.py \
          core/skill_distiller/encryptor.py; do
    [ -f "$f" ] && mv "$f" "distiller/$(basename $f)" && log_ok "$f → distiller/$(basename $f)"
done

# =============================================================================
# 3. 迁移 distiller/persona/（原 core/identity/ + core/tone/）
# =============================================================================
log_step "迁移 core/identity + core/tone → distiller/persona/..."

# identity 文件（跳过 __init__.py，下面统一生成合并版）
for f in core/identity/contact_classifier.py \
          core/identity/relationship_model.py; do
    [ -f "$f" ] && mv "$f" "distiller/persona/$(basename $f)" && log_ok "$f → distiller/persona/$(basename $f)"
done

# tone 文件
for f in core/tone/persona_manager.py \
          core/tone/tone_filter.py; do
    [ -f "$f" ] && mv "$f" "distiller/persona/$(basename $f)" && log_ok "$f → distiller/persona/$(basename $f)"
done

# 合并 identity/__init__.py 与 tone/__init__.py → persona/__init__.py
cat > distiller/persona/__init__.py << 'PERSONA_INIT'
"""
distiller.persona — 人设核心层 (Persona Core)
Shadow Clone 重构自：core/identity + core/tone

子模块：
  contact_classifier  : 联系人分级 (Identity Mapping)
  relationship_model  : 关系人画像建模
  persona_manager     : 核心人设管理（身份底色永不变）
  tone_filter         : 语气滤镜（专业 / 亲和 / 极简）

原始模块说明已合并，详见各子模块文件头注释。
"""
PERSONA_INIT
log_ok "生成合并版 distiller/persona/__init__.py"

# =============================================================================
# 4. 迁移 distiller/reflection/（原 core/reflection/）
# =============================================================================
log_step "迁移 core/reflection → distiller/reflection/..."

for f in core/reflection/__init__.py \
          core/reflection/diff_tracker.py \
          core/reflection/skill_updater.py; do
    [ -f "$f" ] && mv "$f" "distiller/reflection/$(basename $f)" && log_ok "$f → distiller/reflection/$(basename $f)"
done

# =============================================================================
# 5. 迁移 hook/（原 probe/）
# =============================================================================
log_step "迁移 probe → hook/..."

for f in probe/__init__.py \
          probe/base_probe.py; do
    [ -f "$f" ] && mv "$f" "hook/$(basename $f)" && log_ok "$f → hook/$(basename $f)"
done

for f in probe/macos/__init__.py \
          probe/macos/accessibility_probe.py \
          probe/macos/vision_ocr_probe.py; do
    [ -f "$f" ] && mv "$f" "hook/macos/$(basename $f)" && log_ok "$f → hook/macos/$(basename $f)"
done

for f in probe/windows/__init__.py \
          probe/windows/uiautomation_probe.py; do
    [ -f "$f" ] && mv "$f" "hook/windows/$(basename $f)" && log_ok "$f → hook/windows/$(basename $f)"
done

# =============================================================================
# 6. 迁移 hook/overlay/（原 ui/sidebar/）
# =============================================================================
log_step "迁移 ui/sidebar → hook/overlay/..."

for f in ui/sidebar/__init__.py \
          ui/sidebar/main_panel.py \
          ui/sidebar/ghost_text.py; do
    [ -f "$f" ] && mv "$f" "hook/overlay/$(basename $f)" && log_ok "$f → hook/overlay/$(basename $f)"
done

# =============================================================================
# 7. 迁移 hook/overlay/settings/（原 ui/settings/）
# =============================================================================
log_step "迁移 ui/settings → hook/overlay/settings/..."

for f in ui/settings/__init__.py \
          ui/settings/api_config_panel.py \
          ui/settings/tone_selector.py; do
    [ -f "$f" ] && mv "$f" "hook/overlay/settings/$(basename $f)" && log_ok "$f → hook/overlay/settings/$(basename $f)"
done

# =============================================================================
# 8. 迁移 hook/tab_handler.py（原 ui/tab_handler.py）
# =============================================================================
log_step "迁移 ui/tab_handler.py → hook/tab_handler.py..."

[ -f "ui/tab_handler.py" ] && mv "ui/tab_handler.py" "hook/tab_handler.py" && log_ok "ui/tab_handler.py → hook/tab_handler.py"

# ui/__init__.py
[ -f "ui/__init__.py" ] && mv "ui/__init__.py" "hook/__init__.py.ui_orig" && log_warn "ui/__init__.py 已备份为 hook/__init__.py.ui_orig（已有 hook/__init__.py 来自 probe）"

# =============================================================================
# 9. 清理旧目录
# =============================================================================
log_step "清理旧目录..."

rm -rf core/skill_distiller core/identity core/tone core/reflection
rmdir core 2>/dev/null && log_ok "core/ 已清空并删除" || log_warn "core/ 中仍有残留文件，请手动检查"

rm -rf probe/macos probe/windows
rmdir probe 2>/dev/null && log_ok "probe/ 已清空并删除" || log_warn "probe/ 中仍有残留文件，请手动检查"

rm -rf ui/sidebar ui/settings
rmdir ui 2>/dev/null && log_ok "ui/ 已清空并删除" || log_warn "ui/ 中仍有残留文件，请手动检查"

# =============================================================================
# 10. 更新所有 .py 文件的 import 路径
# =============================================================================
log_step "扫描并更新 import 路径..."

PY_FILES=$(find . -name "*.py" \
    ! -path "./.git/*" \
    ! -path "./brain/*" \
    ! -path "./mota/*")

SED_I="sed -i ''"

do_replace() {
    local old="$1"
    local new="$2"
    local count=0
    while IFS= read -r file; do
        if grep -q "$old" "$file" 2>/dev/null; then
            $SED_I "s|${old}|${new}|g" "$file"
            count=$((count + 1))
        fi
    done <<< "$PY_FILES"
    [ $count -gt 0 ] && log_ok "${old}  →  ${new}  (${count} 个文件)"
}

# ── core.skill_distiller → distiller ──
do_replace "from core\.skill_distiller"   "from distiller"
do_replace "import core\.skill_distiller" "import distiller"

# ── core.identity → distiller.persona ──
do_replace "from core\.identity"   "from distiller.persona"
do_replace "import core\.identity" "import distiller.persona"

# ── core.tone → distiller.persona ──
do_replace "from core\.tone"   "from distiller.persona"
do_replace "import core\.tone" "import distiller.persona"

# ── core.reflection → distiller.reflection ──
do_replace "from core\.reflection"   "from distiller.reflection"
do_replace "import core\.reflection" "import distiller.reflection"

# ── core（兜底，捕获其他 core.* 引用）──
do_replace "from core\."   "from distiller."
do_replace "import core\." "import distiller."

# ── probe → hook ──
do_replace "from probe\."   "from hook."
do_replace "import probe\." "import hook."
do_replace "from probe import"   "from hook import"
do_replace "import probe$"       "import hook"

# ── ui.sidebar → hook.overlay ──
do_replace "from ui\.sidebar"   "from hook.overlay"
do_replace "import ui\.sidebar" "import hook.overlay"

# ── ui.settings → hook.overlay.settings ──
do_replace "from ui\.settings"   "from hook.overlay.settings"
do_replace "import ui\.settings" "import hook.overlay.settings"

# ── ui.tab_handler → hook.tab_handler ──
do_replace "from ui\.tab_handler"   "from hook.tab_handler"
do_replace "import ui\.tab_handler" "import hook.tab_handler"

# ── ui（兜底）──
do_replace "from ui\."   "from hook."
do_replace "import ui\." "import hook."

# =============================================================================
# 11. 验证新结构
# =============================================================================
log_step "验证新目录结构..."

EXPECTED_DIRS=(
    "distiller"
    "distiller/persona"
    "distiller/reflection"
    "hook"
    "hook/macos"
    "hook/windows"
    "hook/overlay"
    "hook/overlay/settings"
    "brain"
)

ALL_OK=true
for d in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$d" ]; then
        log_ok "$d/ ✓"
    else
        echo -e "  ${RED}✗  $d/ 缺失！${NC}"
        ALL_OK=false
    fi
done

# =============================================================================
# 完成
# =============================================================================
echo ""
echo -e "${BOLD}${GREEN}"
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║   ✅  Shadow Clone 重构完成！影分身已就位     ║"
echo "  ╚══════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "  新结构速览："
echo -e "  ${CYAN}distiller/${NC}   灵魂引擎（skill + persona + reflection）"
echo -e "  ${CYAN}hook/${NC}        钩子层（probe + overlay + tab）"
echo -e "  ${CYAN}brain/${NC}       智慧中心（未动）"
echo ""

if [ "$ALL_OK" = false ]; then
    echo -e "${YELLOW}⚠  部分目录验证未通过，请手动检查上方日志。${NC}"
    exit 1
fi

echo -e "  下一步建议："
echo -e "  ${BOLD}git diff --stat${NC}   查看变更汇总"
echo -e "  ${BOLD}git add . && git commit -m 'refactor: Shadow Clone restructure'${NC}"
echo ""
