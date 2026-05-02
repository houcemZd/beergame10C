"""Script to add i18n tags to all templates."""
import re, os

BASE = '/home/runner/work/beergameenib.github.io/beergameenib.github.io/beer11C/game/templates'

def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Written: {path}")

# ============================================================
# base.html
# ============================================================
base_path = f'{BASE}/game/base.html'
with open(base_path) as f:
    base = f.read()

# Add {% load i18n %} and {% load static %} at top
base = '{% load i18n %}\n{% load static %}\n' + base.lstrip().replace('{% load static %}\n', '')

# Replace nav links text
base = base.replace(
    '<a href="{% url \'home\' %}">Sessions</a>',
    '<a href="{% url \'home\' %}">{% trans "Sessions" %}</a>'
)
base = base.replace(
    '<a href="/admin/" style="color:var(--distributor-color);">⚙️ Admin</a>',
    '<a href="/admin/" style="color:var(--distributor-color);">⚙️ {% trans "Admin" %}</a>'
)
base = base.replace(
    '<a href="{% url \'new_game\' %}" class="nav-cta">+ New Game</a>',
    '<a href="{% url \'new_game\' %}" class="nav-cta">{% trans "+ New Game" %}</a>'
)

# Replace old JS language switcher button with Django form
old_lang_btn = '''      <!-- Language switcher -->
      <button id="lang-btn" onclick="toggleLang()" title="Switch language / Changer la langue"
        style="background:var(--surface2);border:1px solid var(--border);border-radius:6px;padding:.28rem .6rem;font-size:.72rem;font-weight:700;color:var(--muted);cursor:pointer;font-family:var(--font-mono);transition:all .15s;"
        onmouseover="this.style.borderColor='var(--accent)';this.style.color='var(--accent)'"
        onmouseout="this.style.borderColor='var(--border)';this.style.color='var(--muted)'">
        🌐 EN
      </button>'''

new_lang_form = '''      <!-- Language switcher -->
<form action="{% url 'set_language' %}" method="post" style="display:inline;">
  {% csrf_token %}
  <input type="hidden" name="next" value="{{ request.get_full_path }}">
  <button type="submit" name="language" value="en"
    style="background:{% if LANGUAGE_CODE == 'en' %}var(--surface3){% else %}var(--surface2){% endif %};border:1px solid var(--border);border-radius:6px;padding:.28rem .6rem;font-size:.72rem;font-weight:700;color:{% if LANGUAGE_CODE == 'en' %}var(--accent){% else %}var(--muted){% endif %};cursor:pointer;font-family:var(--font-mono);">EN</button>
  <button type="submit" name="language" value="fr"
    style="background:{% if LANGUAGE_CODE == 'fr' %}var(--surface3){% else %}var(--surface2){% endif %};border:1px solid var(--border);border-radius:6px;padding:.28rem .6rem;font-size:.72rem;font-weight:700;color:{% if LANGUAGE_CODE == 'fr' %}var(--accent){% else %}var(--muted){% endif %};cursor:pointer;font-family:var(--font-mono);">FR</button>
</form>'''

base = base.replace(old_lang_btn, new_lang_form)

# Remove the entire JS language switcher block
# Find the comment marker and the closing </script>
import re
base = re.sub(
    r'\s*<!-- ── Language switcher ──.*?</script>\s*</body>',
    '\n</body>',
    base,
    flags=re.DOTALL
)

write(base_path, base)

# ============================================================
# accounts/login.html  (currently in French, convert to i18n)
# ============================================================
login_path = f'{BASE}/accounts/login.html'
login = '''{% load i18n %}
{% extends "game/base.html" %}
{% block title %}{% trans "Beer Game — Sign In" %}{% endblock %}

{% block extra_head %}
<style>
.landing {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 0;
  min-height: calc(100vh - 56px);
}
@media (max-width: 840px) {
  .landing { grid-template-columns: 1fr; }
  .landing-left { display: none; }
}

/* Left — hero info panel */
.landing-left {
  background: linear-gradient(145deg, #0d0f14 0%, #12151e 100%);
  border-right: 1px solid var(--border);
  padding: 4rem 3rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
.landing-left::before {
  content: \'\';
  position: absolute;
  top: -80px; left: -80px;
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(245,200,66,.06), transparent 70%);
  pointer-events: none;
}
.ll-eyebrow {
  font-family: var(--font-mono);
  font-size: .68rem;
  letter-spacing: .2em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: .6rem;
}
.ll-title {
  font-family: var(--font-mono);
  font-size: 3rem;
  font-weight: 700;
  line-height: 1.05;
  letter-spacing: -.02em;
  margin-bottom: 1rem;
}
.ll-title .accent { color: var(--accent); }
.ll-desc {
  color: var(--muted);
  font-size: .9rem;
  line-height: 1.7;
  max-width: 380px;
  margin-bottom: 2.5rem;
}

.chain-demo {
  display: flex;
  align-items: center;
  gap: .4rem;
  flex-wrap: wrap;
  margin-bottom: 2.5rem;
}
.chain-node {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: .4rem .7rem;
  font-size: .75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: .3rem;
}
.chain-arrow { color: var(--muted); font-size: .75rem; }

.ll-features {
  display: flex;
  flex-direction: column;
  gap: .65rem;
}
.ll-feat {
  display: flex;
  align-items: flex-start;
  gap: .65rem;
  font-size: .82rem;
  color: var(--muted);
}
.ll-feat-icon {
  width: 28px; height: 28px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  font-size: .85rem;
  flex-shrink: 0;
}
.ll-feat-text strong { color: var(--text); }

/* Right — auth card */
.landing-right {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 2.5rem;
  background: var(--surface);
}
.auth-card {
  width: 100%;
  max-width: 360px;
}
.auth-card-title {
  font-family: var(--font-mono);
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: .25rem;
}
.auth-card-sub {
  font-size: .8rem;
  color: var(--muted);
  margin-bottom: 1.75rem;
}
.auth-field { margin-bottom: 1rem; }
.auth-label {
  display: block;
  font-size: .72rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: .08em;
  margin-bottom: .35rem;
  font-weight: 600;
}
.auth-input {
  width: 100%;
  background: var(--surface2);
  border: 1.5px solid var(--border);
  border-radius: 9px;
  color: var(--text);
  padding: .65rem .9rem;
  font-size: .9rem;
  font-family: var(--font-body);
  outline: none;
  transition: border-color .15s, box-shadow .15s;
  box-sizing: border-box;
}
.auth-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(245,200,66,.1);
}
.auth-btn {
  width: 100%;
  padding: .75rem;
  font-size: .95rem;
  font-weight: 700;
  justify-content: center;
  border-radius: 9px;
  margin-top: .25rem;
}
.auth-error {
  background: rgba(239,68,68,.08);
  border: 1px solid rgba(239,68,68,.3);
  border-radius: 8px;
  padding: .6rem .85rem;
  font-size: .8rem;
  color: var(--danger);
  margin-bottom: 1rem;
}
.auth-divider {
  display: flex; align-items: center; gap: .75rem;
  margin: 1.25rem 0;
}
.auth-divider::before, .auth-divider::after {
  content: \'\'; flex: 1; height: 1px; background: var(--border);
}
.auth-divider span { font-size: .72rem; color: var(--muted); white-space: nowrap; }
.auth-register-link {
  text-align: center;
  font-size: .82rem;
  color: var(--muted);
  margin-top: 1.25rem;
}
.auth-register-link a { color: var(--accent); font-weight: 600; }
</style>
{% endblock %}

{% block content %}
<div class="landing">

  <!-- ── Left: Hero panel ─────────────────────────────────────────────────── -->
  <div class="landing-left">
    <div class="ll-eyebrow">{% trans "MIT Supply Chain Simulation" %}</div>
    <h1 class="ll-title">THE <span class="accent">BEER</span><br>GAME</h1>
    <p class="ll-desc">
      {% blocktrans %}Real-time multiplayer simulation. Manage your supply chain link, place orders, and discover why small demand variations create large oscillations — the bullwhip effect.{% endblocktrans %}
    </p>

    <div class="chain-demo">
      <div class="chain-node">👤 {% trans "Customer" %}</div>
      <span class="chain-arrow">→</span>
      <div class="chain-node" style="border-color:rgba(245,200,66,.4); color:var(--accent);">🛒 {% trans "Retailer" %}</div>
      <span class="chain-arrow">⇄</span>
      <div class="chain-node" style="border-color:rgba(59,130,246,.4); color:#60a5fa;">🏪 {% trans "Wholesaler" %}</div>
      <span class="chain-arrow">⇄</span>
      <div class="chain-node" style="border-color:rgba(168,85,247,.4); color:#c084fc;">🚚 {% trans "Distributor" %}</div>
      <span class="chain-arrow">⇄</span>
      <div class="chain-node" style="border-color:rgba(34,197,94,.4); color:var(--success);">🏭 {% trans "Factory" %}</div>
    </div>

    <div class="ll-features">
      <div class="ll-feat">
        <div class="ll-feat-icon">⚡</div>
        <div class="ll-feat-text"><strong>{% trans "Real-time" %}</strong> — {% trans "WebSockets for a smooth and simultaneous experience" %}</div>
      </div>
      <div class="ll-feat">
        <div class="ll-feat-icon">👥</div>
        <div class="ll-feat-text"><strong>{% trans "5 players" %}</strong> — {% trans "Customer, Retailer, Wholesaler, Distributor, Factory" %}</div>
      </div>
      <div class="ll-feat">
        <div class="ll-feat-icon">📊</div>
        <div class="ll-feat-text"><strong>{% trans "Bullwhip analysis" %}</strong> — {% trans "Charts and statistics at game end" %}</div>
      </div>
      <div class="ll-feat">
        <div class="ll-feat-icon">📱</div>
        <div class="ll-feat-text"><strong>{% trans "Multi-device" %}</strong> — {% trans "Play from any screen on the network" %}</div>
      </div>
    </div>
  </div>

  <!-- ── Right: Auth card ──────────────────────────────────────────────────── -->
  <div class="landing-right">
    <div class="auth-card">

      <div class="auth-card-title">{% trans "Sign In" %}</div>
      <div class="auth-card-sub">{% trans "Sign in to play or create a game" %}</div>

      {% if messages %}
        {% for message in messages %}
        <div class="auth-error">{{ message }}</div>
        {% endfor %}
      {% endif %}

      <form method="POST">
        {% csrf_token %}

        <div class="auth-field">
          <label class="auth-label" for="username">{% trans "Username" %}</label>
          <input class="auth-input" type="text" id="username" name="username"
                 placeholder="{% trans 'Your username' %}" autocomplete="username" autofocus
                 value="{{ request.POST.username|default:\'\' }}" />
        </div>

        <div class="auth-field">
          <label class="auth-label" for="password">{% trans "Password" %}</label>
          <input class="auth-input" type="password" id="password" name="password"
                 placeholder="••••••••" autocomplete="current-password" />
        </div>

        <button type="submit" class="btn btn-primary auth-btn">
          {% trans "Sign In →" %}
        </button>
      </form>

      <div class="auth-divider"><span>{% trans "No account yet?" %}</span></div>

      <a href="{% url \'register\' %}" class="btn btn-ghost" style="width:100%; justify-content:center; border-radius:9px; padding:.7rem; font-size:.9rem;">
        {% trans "Create a free account" %}
      </a>

    </div>
  </div>
</div>
{% endblock %}
'''
write(login_path, login)

# ============================================================
# accounts/register.html
# ============================================================
reg_path = f'{BASE}/accounts/register.html'
with open(reg_path) as f:
    reg = f.read()

# Add load i18n before extends
reg = '{% load i18n %}\n' + reg

# Title
reg = reg.replace('{% block title %}Créer un compte — Beer Game{% endblock %}',
                  '{% block title %}{% trans "Create Account — Beer Game" %}{% endblock %}')

# Logo sub
reg = reg.replace('<div class="auth-logo-sub">Créer un compte joueur</div>',
                  '<div class="auth-logo-sub">{% trans "Create a player account" %}</div>')

# Labels
reg = reg.replace('<label class="auth-label" for="first_name">Prénom</label>',
                  '<label class="auth-label" for="first_name">{% trans "First name" %}</label>')
reg = reg.replace('<label class="auth-label" for="username">Identifiant</label>',
                  '<label class="auth-label" for="username">{% trans "Username" %}</label>')
reg = reg.replace('<label class="auth-label" for="email">Email <span style="color:var(--muted);font-weight:400;">(optionnel)</span></label>',
                  '<label class="auth-label" for="email">{% trans "Email (optional)" %}</label>')
reg = reg.replace('<label class="auth-label" for="password1">Mot de passe</label>',
                  '<label class="auth-label" for="password1">{% trans "Password" %}</label>')
reg = reg.replace('placeholder="8 caractères minimum"',
                  'placeholder="{% trans \'8 characters minimum\' %}"')
reg = reg.replace('<label class="auth-label" for="password2">Confirmer le mot de passe</label>',
                  '<label class="auth-label" for="password2">{% trans "Confirm password" %}</label>')
reg = reg.replace('placeholder="Répétez le mot de passe"',
                  'placeholder="{% trans \'Repeat the password\' %}"')

# Submit button
reg = reg.replace('<button type="submit" class="btn btn-primary auth-btn">\n        Créer mon compte →\n      </button>',
                  '<button type="submit" class="btn btn-primary auth-btn">\n        {% trans "Create my account →" %}\n      </button>')

# Register link
reg = reg.replace('Déjà inscrit ? <a href="{% url \'login\' %}">Se connecter</a>',
                  '{% trans "Already registered?" %} <a href="{% url \'login\' %}">{% trans "Sign in" %}</a>')

# JS strings for password strength
reg = reg.replace("t:'Très faible'", "t:gettext('Very weak')")
reg = reg.replace("t:'Faible'", "t:gettext('Weak')")
reg = reg.replace("t:'Moyen'", "t:gettext('Medium')")
reg = reg.replace("t:'Bon'", "t:gettext('Good')")
reg = reg.replace("t:'Excellent'", "t:gettext('Excellent')")

write(reg_path, reg)

# ============================================================
# accounts/profile.html
# ============================================================
prof_path = f'{BASE}/accounts/profile.html'
with open(prof_path) as f:
    prof = f.read()

prof = '{% load i18n %}\n' + prof

prof = prof.replace('<div class="stat-pill">🎮 <strong>{{ created_games }}</strong> games created</div>',
                    '<div class="stat-pill">🎮 <strong>{{ created_games }}</strong> {% trans "games created" %}</div>')
prof = prof.replace('<div class="stat-pill">🎭 <strong>{{ played_roles|length }}</strong> roles played</div>',
                    '<div class="stat-pill">🎭 <strong>{{ played_roles|length }}</strong> {% trans "roles played" %}</div>')

prof = prof.replace('<div class="card-title">✏️ Edit Profile</div>',
                    '<div class="card-title">✏️ {% trans "Edit Profile" %}</div>')
prof = prof.replace(
    '<label style="font-size:.72rem; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; display:block; margin-bottom:.35rem;">Display Name</label>',
    '<label style="font-size:.72rem; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; display:block; margin-bottom:.35rem;">{% trans "Display Name" %}</label>'
)
prof = prof.replace('placeholder="Your name"', 'placeholder="{% trans \'Your name\' %}"')
prof = prof.replace('<button type="submit" class="btn btn-primary" style="align-self:flex-start;">Save Changes</button>',
                    '<button type="submit" class="btn btn-primary" style="align-self:flex-start;">{% trans "Save Changes" %}</button>')

prof = prof.replace('<div class="card-title">🎭 Recent Roles Played</div>',
                    '<div class="card-title">🎭 {% trans "Recent Roles Played" %}</div>')

prof = prof.replace('<div class="card-title">🔐 Account Actions</div>',
                    '<div class="card-title">🔐 {% trans "Account Actions" %}</div>')

prof = prof.replace('<button type="submit" class="btn btn-ghost">🚪 Disconnect / Log out</button>',
                    '<button type="submit" class="btn btn-ghost">🚪 {% trans "Disconnect / Log out" %}</button>')
prof = prof.replace('<a href="{% url \'home\' %}" class="btn btn-ghost">← Back to Sessions</a>',
                    '<a href="{% url \'home\' %}" class="btn btn-ghost">← {% trans "Back to Sessions" %}</a>')

prof = prof.replace('<div class="danger-zone-title">⚠️ Danger Zone</div>',
                    '<div class="danger-zone-title">⚠️ {% trans "Danger Zone" %}</div>')
prof = prof.replace(
    'Permanently delete your account and all associated data. This action cannot be undone.',
    '{% trans "Permanently delete your account and all associated data. This action cannot be undone." %}'
)
prof = prof.replace(
    "onsubmit=\"return confirm('Are you sure? This will permanently delete your account and cannot be undone.');\"",
    "onsubmit=\"return confirm('{% trans \"Are you sure? This will permanently delete your account and cannot be undone.\" %}')\""
)
prof = prof.replace('<button type="submit" class="btn btn-danger">🗑️ Delete My Account</button>',
                    '<button type="submit" class="btn btn-danger">🗑️ {% trans "Delete My Account" %}</button>')

write(prof_path, prof)

print("Done with accounts templates")
