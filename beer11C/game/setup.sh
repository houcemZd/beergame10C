#!/bin/bash
# ── Beer Game — Setup & Update ─────────────────────────────────────────────────
set -e

# ── Colours ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC}  $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC}  $1"; }
info() { echo -e "  ${CYAN}→${NC}  $1"; }
err()  { echo -e "  ${RED}✗${NC}  $1"; }
sep()  { echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }

echo ""
echo -e "${BOLD}🍺  Beer Game — Setup & Update${NC}"
sep

# ── Detect project root (where manage.py lives) ────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/manage.py" ]; then
  PROJECT_ROOT="$SCRIPT_DIR"
elif [ -f "manage.py" ]; then
  PROJECT_ROOT="$(pwd)"
else
  err "Cannot find manage.py — run this script from your Django project root."
  exit 1
fi
info "Project root: $PROJECT_ROOT"

# ── Detect app name (folder containing models.py and consumers.py) ─────────────
APP_DIR=""
for d in "$PROJECT_ROOT"/*/; do
  if [ -f "$d/models.py" ] && [ -f "$d/consumers.py" ]; then
    APP_DIR="$d"
    APP_NAME="$(basename "$d")"
    break
  fi
done
if [ -z "$APP_DIR" ]; then
  err "Cannot find your game app (folder with models.py + consumers.py)."
  exit 1
fi
ok "Game app: $APP_NAME"

# ── Detect settings.py ─────────────────────────────────────────────────────────
SETTINGS_FILE=""
for f in "$PROJECT_ROOT"/*/settings.py "$PROJECT_ROOT"/settings.py; do
  if [ -f "$f" ]; then
    SETTINGS_FILE="$f"
    break
  fi
done
if [ -z "$SETTINGS_FILE" ]; then
  err "Cannot find settings.py"
  exit 1
fi
ok "Settings: $(basename $(dirname $SETTINGS_FILE))/settings.py"

sep

# ── 1. Virtual environment ──────────────────────────────────────────────────────
info "Checking virtual environment..."
if [ ! -d "$PROJECT_ROOT/venv" ]; then
  info "Creating virtual environment..."
  python3 -m venv "$PROJECT_ROOT/venv"
fi
source "$PROJECT_ROOT/venv/bin/activate"
ok "Virtual environment active"

# ── 2. Dependencies ─────────────────────────────────────────────────────────────
info "Installing / updating Python dependencies..."
pip install -q -r "$PROJECT_ROOT/requirements.txt"

# Ensure daphne is installed (required for WebSocket support)
if ! python3 -c "import daphne" 2>/dev/null; then
  info "Installing daphne (ASGI server for WebSockets)..."
  pip install -q daphne
fi
ok "Dependencies up to date (daphne ✓)"

# ── 3. Copy updated project files ──────────────────────────────────────────────
sep
info "Copying updated source files..."

TEMPLATES_DIR="$APP_DIR/templates/$APP_NAME"
mkdir -p "$TEMPLATES_DIR"

# Helper: copy file and report
copy_file() {
  local src="$1" dst="$2"
  if [ -f "$src" ]; then
    cp "$src" "$dst"
    ok "$(basename $src) → ${dst#$PROJECT_ROOT/}"
  else
    warn "Not found (skip): $src"
  fi
}

# Python source files
copy_file "$SCRIPT_DIR/models.py"         "$APP_DIR/models.py"
copy_file "$SCRIPT_DIR/consumers.py"      "$APP_DIR/consumers.py"
copy_file "$SCRIPT_DIR/services.py"       "$APP_DIR/services.py"
copy_file "$SCRIPT_DIR/views.py"          "$APP_DIR/views.py"
copy_file "$SCRIPT_DIR/urls.py"           "$APP_DIR/urls.py"
copy_file "$SCRIPT_DIR/accounts_views.py" "$APP_DIR/accounts_views.py"

# HTML templates — game templates
copy_file "$SCRIPT_DIR/play.html"         "$TEMPLATES_DIR/play.html"
copy_file "$SCRIPT_DIR/lobby.html"        "$TEMPLATES_DIR/lobby.html"
copy_file "$SCRIPT_DIR/home.html"         "$TEMPLATES_DIR/home.html"
copy_file "$SCRIPT_DIR/base.html"         "$TEMPLATES_DIR/base.html"

# Accounts templates (login / register)
ACCOUNTS_TEMPLATES_DIR="$APP_DIR/templates/accounts"
mkdir -p "$ACCOUNTS_TEMPLATES_DIR"
copy_file "$SCRIPT_DIR/login.html"    "$ACCOUNTS_TEMPLATES_DIR/login.html"
copy_file "$SCRIPT_DIR/register.html" "$ACCOUNTS_TEMPLATES_DIR/register.html"

# Optional templates (copy if present)
for tmpl in join.html new_game.html game_init.html results.html dashboard.html customer_play.html customer_view.html client_view.html; do
  [ -f "$SCRIPT_DIR/$tmpl" ] && copy_file "$SCRIPT_DIR/$tmpl" "$TEMPLATES_DIR/$tmpl"
done

# ── 4. Apply migration for new PlayerSession fields ────────────────────────────
sep
info "Checking database migrations..."

MIGRATIONS_DIR="$APP_DIR/migrations"
mkdir -p "$MIGRATIONS_DIR"
touch "$MIGRATIONS_DIR/__init__.py" 2>/dev/null || true

# Check if turn_phase column already exists
NEED_PHASE_MIGRATION=false
python3 - << 'PYCHECK'
import os, sys, django
sys.path.insert(0, os.environ.get('PROJECT_ROOT', '.'))
# Find settings module
import glob
settings_files = glob.glob('*/settings.py') + glob.glob('settings.py')
for sf in settings_files:
    mod = sf.replace('/', '.').replace('.py', '')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', mod)
    break
try:
    django.setup()
    from django.db import connection
    cols = [c.name for c in connection.introspection.get_table_description(
        connection.cursor(), 'game_playersession'
    )]
    if 'turn_phase' in cols:
        sys.exit(0)   # already exists
    else:
        sys.exit(1)   # needs migration
except Exception:
    sys.exit(1)
PYCHECK
PHASE_CHECK=$?

if [ $PHASE_CHECK -ne 0 ]; then
  NEED_PHASE_MIGRATION=true
  info "New PlayerSession fields detected — creating migration..."

  # Find last migration number
  LAST_NUM=$(ls "$MIGRATIONS_DIR"/[0-9]*.py 2>/dev/null | sort | tail -1 | grep -o '[0-9]\{4\}' | head -1)
  if [ -z "$LAST_NUM" ]; then
    NEXT_NUM="0002"
    DEPENDS_ON="0001_initial"
  else
    NEXT_NUM=$(printf "%04d" $((10#$LAST_NUM + 1)))
    DEPENDS_ON="$(ls "$MIGRATIONS_DIR"/[0-9]*.py | sort | tail -1 | xargs basename | sed 's/.py//')"
  fi

  MIGRATION_FILE="$MIGRATIONS_DIR/${NEXT_NUM}_add_playersession_phase_fields.py"
  cat > "$MIGRATION_FILE" << MIGEOF
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('$APP_NAME', '$DEPENDS_ON')]
    operations = [
        migrations.AddField(
            model_name='playersession', name='turn_phase',
            field=models.CharField(max_length=10, default='idle'),
        ),
        migrations.AddField(
            model_name='playersession', name='pending_received_qty',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playersession', name='pending_order_qty',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playersession', name='pending_ship_qty',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
MIGEOF
  ok "Migration created: $NEXT_NUM"
else
  ok "PlayerSession fields already present — no migration needed"
fi

# Run all pending migrations
cd "$PROJECT_ROOT"
python manage.py migrate --run-syncdb -v 0
ok "Database up to date"

# ── 5. Detect local IP and patch settings.py ───────────────────────────────────
sep
info "Configuring network settings..."

# Get local IP (works on Mac and Linux)
LOCAL_IP=""
if command -v ipconfig &>/dev/null; then
  # macOS
  LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "")
fi
if [ -z "$LOCAL_IP" ] && command -v hostname &>/dev/null; then
  # Linux
  LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
fi
if [ -z "$LOCAL_IP" ]; then
  LOCAL_IP=$(python3 -c "import socket; s=socket.socket(); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2>/dev/null || echo "")
fi

if [ -n "$LOCAL_IP" ]; then
  ok "Local IP: $LOCAL_IP"
else
  warn "Could not detect local IP — cross-device access may not work"
  LOCAL_IP="0.0.0.0"
fi

# Patch ALLOWED_HOSTS in settings.py
if grep -q "ALLOWED_HOSTS" "$SETTINGS_FILE"; then
  # Check if our IP is already there
  if ! grep -q "$LOCAL_IP" "$SETTINGS_FILE"; then
    info "Adding $LOCAL_IP to ALLOWED_HOSTS..."
    # Replace ALLOWED_HOSTS = [...] with version including our IP
    python3 - "$SETTINGS_FILE" "$LOCAL_IP" << 'PYEOF'
import sys, re

settings_path = sys.argv[1]
local_ip      = sys.argv[2]

with open(settings_path) as f:
    content = f.read()

# Find ALLOWED_HOSTS = [...] and add our IP if not present
pattern = r"(ALLOWED_HOSTS\s*=\s*\[)([^\]]*?)(\])"
def add_host(m):
    existing = m.group(2)
    if local_ip in existing:
        return m.group(0)
    # Strip trailing whitespace/newlines from existing entries
    entries = [e.strip() for e in existing.split(',') if e.strip()]
    entries.extend([f"'{local_ip}'", "'localhost'", "'127.0.0.1'"])
    unique = list(dict.fromkeys(entries))  # deduplicate preserving order
    return m.group(1) + '\n    ' + ',\n    '.join(unique) + '\n' + m.group(3)

new_content = re.sub(pattern, add_host, content, flags=re.DOTALL)

# Add CSRF_TRUSTED_ORIGINS if not present
if 'CSRF_TRUSTED_ORIGINS' not in new_content:
    new_content += f"\n# Added by setup.sh for cross-device access\nCSRF_TRUSTED_ORIGINS = ['http://{local_ip}:8000', 'http://localhost:8000']\n"
elif local_ip not in new_content.split('CSRF_TRUSTED_ORIGINS')[1].split('\n')[0:5]:
    # Add our IP to existing list
    new_content = re.sub(
        r"(CSRF_TRUSTED_ORIGINS\s*=\s*\[)([^\]]*?)(\])",
        lambda m: m.group(1) + m.group(2).rstrip() + f", 'http://{local_ip}:8000'" + m.group(3),
        new_content, flags=re.DOTALL
    )

with open(settings_path, 'w') as f:
    f.write(new_content)

print("patched")
PYEOF
    ok "settings.py patched for cross-device access"
  else
    ok "ALLOWED_HOSTS already contains $LOCAL_IP"
  fi
fi

# Patch LOGIN_URL so @login_required redirects to our login page
python3 - "$SETTINGS_FILE" << 'PYEOF'
import sys, re

settings_path = sys.argv[1]
with open(settings_path) as f:
    content = f.read()

additions = ""
if 'LOGIN_URL' not in content:
    additions += "\n# Auth redirects — added by setup.sh\nLOGIN_URL = '/accounts/login/'\nLOGIN_REDIRECT_URL = '/'\nLOGOUT_REDIRECT_URL = '/accounts/login/'\n"

if additions:
    with open(settings_path, 'a') as f:
        f.write(additions)
    print("patched auth settings")
PYEOF
ok "Auth redirect URLs configured"

# ── 6. Patch channel layer in settings.py (InMemory fallback if no Redis) ───────
info "Checking channel layer (Redis / InMemory)..."

REDIS_OK=false
if command -v redis-cli &>/dev/null && redis-cli ping &>/dev/null 2>&1; then
  REDIS_OK=true
fi

# Check if channels_redis is installed
python3 -c "import channels_redis" 2>/dev/null && REDIS_PKG=true || REDIS_PKG=false

if $REDIS_OK && $REDIS_PKG; then
  ok "Redis is running — full multiplayer enabled"
  CHANNEL_LAYER='CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
    }
}'
else
  warn "Redis not available — using InMemoryChannelLayer (single-machine only)"
  warn "For real cross-device multiplayer: docker run -p 6379:6379 redis:alpine"
  warn "Then re-run setup.sh"
  CHANNEL_LAYER='CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}'
fi

# Write channel layer to settings if not already correct
if ! grep -q "CHANNEL_LAYERS" "$SETTINGS_FILE"; then
  echo "" >> "$SETTINGS_FILE"
  echo "# Channel layer — added by setup.sh" >> "$SETTINGS_FILE"
  echo "$CHANNEL_LAYER" >> "$SETTINGS_FILE"
  ok "Channel layer added to settings.py"
else
  # Update existing
  python3 - "$SETTINGS_FILE" "$REDIS_OK" "$REDIS_PKG" << 'PYEOF'
import sys, re

settings_path = sys.argv[1]
redis_ok      = sys.argv[2] == 'true'
redis_pkg     = sys.argv[3] == 'true'

with open(settings_path) as f:
    content = f.read()

if redis_ok and redis_pkg:
    layer = '''CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
    }
}'''
else:
    layer = '''CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}'''

new_content = re.sub(
    r'CHANNEL_LAYERS\s*=\s*\{[^}]*\{[^}]*\}[^}]*\}',
    layer,
    content,
    flags=re.DOTALL
)

with open(settings_path, 'w') as f:
    f.write(new_content)
PYEOF
  ok "Channel layer configured"
fi

# ── 7. Offer to clear stale sessions ───────────────────────────────────────────
sep
SESSION_COUNT=$(python3 -c "
import os, sys, django
sys.path.insert(0, '.')
import glob
for sf in glob.glob('*/settings.py') + ['settings.py']:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', sf.replace('/', '.').replace('.py', ''))
    break
try:
    django.setup()
    from game.models import GameSession
    print(GameSession.objects.count())
except:
    print(0)
" 2>/dev/null || echo "0")

if [ "$SESSION_COUNT" -gt 10 ]; then
  echo ""
  warn "You have $SESSION_COUNT sessions in the database."
  echo -e "     Delete all and start fresh? ${BOLD}[y/N]${NC} " && read -r REPLY
  if [[ "$REPLY" =~ ^[Yy]$ ]]; then
    python3 -c "
import os, sys, django
sys.path.insert(0, '.')
import glob
for sf in glob.glob('*/settings.py') + ['settings.py']:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', sf.replace('/', '.').replace('.py', ''))
    break
django.setup()
from game.models import GameSession
n = GameSession.objects.count()
GameSession.objects.all().delete()
print(f'Deleted {n} sessions.')
" 2>/dev/null
    ok "All sessions cleared"
  else
    ok "Keeping existing sessions"
  fi
else
  ok "$SESSION_COUNT existing session(s) — keeping"
fi

# ── 8. Print summary and start ─────────────────────────────────────────────────
sep
echo ""
echo -e "${BOLD}${GREEN}✅  All done!${NC}"
echo ""
echo -e "  ${BOLD}This machine:${NC}   http://127.0.0.1:8000"
if [ -n "$LOCAL_IP" ] && [ "$LOCAL_IP" != "0.0.0.0" ]; then
echo -e "  ${BOLD}Other devices:${NC}  http://$LOCAL_IP:8000"
fi
echo ""
echo -e "  ${BOLD}Roles:${NC}  👤 Customer  🛒 Retailer  🏪 Wholesaler  🚚 Distributor  🏭 Factory"
echo -e "  ${BOLD}Flow:${NC}   Receive → Ship → Order → ${CYAN}Ready for next week${NC}"
echo ""
echo -e "  ${YELLOW}Using Daphne (ASGI) — WebSockets fully supported${NC}"
sep
echo ""

# Detect Django project module (folder containing settings.py + asgi.py)
ASGI_MODULE=""
for d in "$PROJECT_ROOT"/*/; do
  if [ -f "$d/asgi.py" ] && [ -f "$d/settings.py" ]; then
    ASGI_MODULE="$(basename "$d").asgi:application"
    break
  fi
done

if [ -z "$ASGI_MODULE" ]; then
  warn "Cannot find asgi.py — falling back to manage.py runserver (no WebSockets!)"
  warn "Create <project>/asgi.py with Django Channels routing for full functionality."
  cd "$PROJECT_ROOT"
  python manage.py runserver 0.0.0.0:8000
else
  ok "ASGI module: $ASGI_MODULE"
  cd "$PROJECT_ROOT"
  # Daphne: bind to all interfaces, port 8000
  daphne -b 0.0.0.0 -p 8000 "$ASGI_MODULE"
fi
