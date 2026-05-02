import re, os

BASE = '/home/runner/work/beergameenib.github.io/beergameenib.github.io/beer11C/game/templates'

def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Written: {path}")

def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def add_i18n(content):
    """Add {% load i18n %} at very top if not already there."""
    if '{% load i18n %}' not in content:
        content = '{% load i18n %}\n' + content
    return content

# ============================================================
# home.html  — already has French text mixed in; map everything to trans
# ============================================================
p = f'{BASE}/game/home.html'
c = read(p)
c = add_i18n(c)

replacements = [
    # Title
    ('{% block title %}Sessions — Beer Game{% endblock %}',
     '{% block title %}{% trans "Sessions — Beer Game" %}{% endblock %}'),
    ('{% block title %}Sessions – Beer Game{% endblock %}',
     '{% block title %}{% trans "Sessions — Beer Game" %}{% endblock %}'),
    # Header
    ('<h1 class="sessions-heading">My Sessions</h1>',
     '<h1 class="sessions-heading">{% trans "My Sessions" %}</h1>'),
    ('<h1 class="sessions-heading">Mes sessions</h1>',
     '<h1 class="sessions-heading">{% trans "My Sessions" %}</h1>'),
    # Buttons
    ('<a href="{% url \'new_game\' %}" class="btn btn-primary">+ New Game</a>',
     '<a href="{% url \'new_game\' %}" class="btn btn-primary">{% trans "+ New Game" %}</a>'),
    ('<a href="{% url \'new_game\' %}" class="btn btn-primary">+ Nouvelle partie</a>',
     '<a href="{% url \'new_game\' %}" class="btn btn-primary">{% trans "+ New Game" %}</a>'),
    # Empty state
    ('No sessions yet.',
     '{% trans "No sessions yet." %}'),
    ('Aucune session pour l\'instant.',
     '{% trans "No sessions yet." %}'),
    ('Create your first game!',
     '{% trans "Create your first game!" %}'),
    ('Créez votre première partie !',
     '{% trans "Create your first game!" %}'),
    # Role labels
    ('>Retailer<', '>{% trans "Retailer" %}<'),
    ('>Wholesaler<', '>{% trans "Wholesaler" %}<'),
    ('>Distributor<', '>{% trans "Distributor" %}<'),
    ('>Factory<', '>{% trans "Factory" %}<'),
    # Status
    ('>Waiting<', '>{% trans "Waiting" %}<'),
    ('>In progress<', '>{% trans "In progress" %}<'),
    ('>Finished<', '>{% trans "Finished" %}<'),
    # Actions
    ('>Resume<', '>{% trans "Resume" %}<'),
    ('>Join<', '>{% trans "Join" %}<'),
    ('>View<', '>{% trans "View" %}<'),
    ('>Delete<', '>{% trans "Delete" %}<'),
    ('>Settings<', '>{% trans "Settings" %}<'),
    ('>Results<', '>{% trans "Results" %}<'),
    # Delete dialog (was in French)
    ('Supprimer la partie ?', '{% trans "Delete this game?" %}'),
    ('Supprimer', '{% trans "Delete" %}'),
    ('Annuler', '{% trans "Cancel" %}'),
    ('Cette action est irréversible.', '{% trans "This action cannot be undone." %}'),
    # Stats labels
    ('>Rounds<', '>{% trans "Rounds" %}<'),
    ('>Players<', '>{% trans "Players" %}<'),
    ('>Created<', '>{% trans "Created" %}<'),
    ('>Instructor<', '>{% trans "Instructor" %}<'),
]

for old, new in replacements:
    c = c.replace(old, new)

write(p, c)

# ============================================================
# new_game.html
# ============================================================
p = f'{BASE}/game/new_game.html'
c = read(p)
c = add_i18n(c)

reps = [
    ('New Game', '{% trans "New Game" %}'),
    ('Game Name', '{% trans "Game Name" %}'),
    ('Enter game name', '{% trans "Enter game name" %}'),
    ('Number of Rounds', '{% trans "Number of Rounds" %}'),
    ('Order Delay (weeks)', '{% trans "Order Delay (weeks)" %}'),
    ('Shipping Delay (weeks)', '{% trans "Shipping Delay (weeks)" %}'),
    ('Initial Inventory', '{% trans "Initial Inventory" %}'),
    ('Include Customer', '{% trans "Include Customer" %}'),
    ('Create Game', '{% trans "Create Game" %}'),
    ('Cancel', '{% trans "Cancel" %}'),
    ('Back', '{% trans "Back" %}'),
    ('Advanced Settings', '{% trans "Advanced Settings" %}'),
    ('Customer Demand', '{% trans "Customer Demand" %}'),
    ('Holding Cost', '{% trans "Holding Cost" %}'),
    ('Backorder Cost', '{% trans "Backorder Cost" %}'),
    ('Demand Pattern', '{% trans "Demand Pattern" %}'),
    ('Custom Sequence', '{% trans "Custom Sequence" %}'),
]
for old, new in reps:
    # Only replace where not already wrapped
    c = c.replace(f'>{old}<', f'>{new}<')
    c = c.replace(f'"{old}"', f'"{new}"')

write(p, c)

# ============================================================
# join.html
# ============================================================
p = f'{BASE}/game/join.html'
c = read(p)
c = add_i18n(c)
reps = [
    ('>Join Game<', '>{% trans "Join Game" %}<'),
    ('>Join<', '>{% trans "Join" %}<'),
    ('>Back<', '>{% trans "Back" %}<'),
    ('>Role taken<', '>{% trans "Role taken" %}<'),
    ('>Available<', '>{% trans "Available" %}<'),
    ('>Taken<', '>{% trans "Taken" %}<'),
]
for old, new in reps:
    c = c.replace(old, new)
write(p, c)

# ============================================================
# join_taken.html
# ============================================================
p = f'{BASE}/game/join_taken.html'
if os.path.exists(p):
    c = read(p)
    c = add_i18n(c)
    c = c.replace('>Role already taken<', '>{% trans "Role already taken" %}<')
    c = c.replace('>Back to Lobby<', '>{% trans "Back to Lobby" %}<')
    write(p, c)

# ============================================================
# instructor.html
# ============================================================
p = f'{BASE}/game/instructor.html'
if os.path.exists(p):
    c = read(p)
    c = add_i18n(c)
    c = c.replace('>Instructor Dashboard<', '>{% trans "Instructor Dashboard" %}<')
    c = c.replace('>Start Game<', '>{% trans "Start Game" %}<')
    c = c.replace('>Reset Game<', '>{% trans "Reset Game" %}<')
    c = c.replace('>End Game<', '>{% trans "End Game" %}<')
    write(p, c)

# ============================================================
# dashboard.html
# ============================================================
p = f'{BASE}/game/dashboard.html'
if os.path.exists(p):
    c = read(p)
    c = add_i18n(c)
    write(p, c)

# ============================================================
# client_view.html
# ============================================================
p = f'{BASE}/game/client_view.html'
if os.path.exists(p):
    c = read(p)
    c = add_i18n(c)
    write(p, c)

# ============================================================
# customer_view.html
# ============================================================
p = f'{BASE}/game/customer_view.html'
if os.path.exists(p):
    c = read(p)
    c = add_i18n(c)
    write(p, c)

print("Done with game templates (simple ones)")
