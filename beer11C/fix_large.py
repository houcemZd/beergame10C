"""Carefully update large templates with i18n tags - only in HTML content, not JS."""
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
    if '{% load i18n %}' not in content:
        content = '{% load i18n %}\n' + content
    return content

def safe_replace_tag_text(content, text, trans_text=None):
    """Replace >text< in HTML (not inside JS strings)."""
    if trans_text is None:
        trans_text = f'{{% trans "{text}" %}}'
    return content.replace(f'>{text}<', f'>{trans_text}<')

def safe_replace_attr(content, attr_name, old_val, new_val=None):
    """Replace attribute value."""
    if new_val is None:
        new_val = f'{{% trans "{old_val}" %}}'
    # Match placeholder="old_val" or title="old_val"
    content = content.replace(f'{attr_name}="{old_val}"', f'{attr_name}="{new_val}"')
    return content

# ============================================================
# lobby.html — carefully
# ============================================================
p = f'{BASE}/game/lobby.html'
c = read(p)
c = add_i18n(c)

# HTML text content only (not JS)
html_texts = [
    'Game Lobby',
    'Waiting for players...',
    'Start Game',
    'Leave Game',
    'Copy Link',
    'Copied!',
    'Players',
    'Chat',
    'Send',
    'Game Settings',
    'Join Link',
    'Share this link',
    'No messages yet.',
    'Waiting for the game to start...',
    'Game will start shortly...',
    'Ready',
    'Waiting',
]
for t in html_texts:
    c = c.replace(f'>{t}<', f'>{{% trans "{t}" %}}<')

# Placeholder attributes
for t in ['Type a message...']:
    c = c.replace(f'placeholder="{t}"', f'placeholder="{{% trans "{t}" %}}"')

# Specific label text that might appear as span text
c = c.replace('>Rounds:<', '>{% trans "Rounds:" %}<')
c = c.replace('>Delay:<', '>{% trans "Delay:" %}<')
c = c.replace('>Inventory:<', '>{% trans "Inventory:" %}<')
c = c.replace('>Status:<', '>{% trans "Status:" %}<')

write(p, c)

# ============================================================
# results.html — carefully
# ============================================================
p = f'{BASE}/game/results.html'
c = read(p)
c = add_i18n(c)

html_texts = [
    'Game Results',
    'Total Cost',
    'Holding Cost',
    'Backorder Cost',
    'Inventory History',
    'Order History',
    'Demand History',
    'Bullwhip Effect',
    'Bullwhip Ratio',
    'Download CSV',
    'Back to Sessions',
    'Play Again',
    'Player',
    'Role',
    'Retailer',
    'Wholesaler',
    'Distributor',
    'Factory',
    'Customer',
    'Cost per Round',
    'Cumulative Cost',
    'Supply Chain Analysis',
    'Game Summary',
    'Duration',
    'Total Rounds',
    'Winner',
    'Best Player',
    'Performance',
    'Results',
    'Game Over',
    'View Results',
]
for t in html_texts:
    c = c.replace(f'>{t}<', f'>{{% trans "{t}" %}}<')

# Round label that appears as text (but not in JS variable)
# Replace only ">Round<" (as HTML text node)
c = c.replace('>Round<', '>{% trans "Round" %}<')

write(p, c)

# ============================================================
# customer_play.html — carefully
# ============================================================
p = f'{BASE}/game/customer_play.html'
c = read(p)
c = add_i18n(c)

html_texts = [
    'Customer Dashboard',
    'Place Demand',
    'Submit Demand',
    'Current Round',
    'Waiting for other players...',
    'Game Over',
    'View Results',
    'Demand History',
    'Chat',
    'Send',
    'Customer',
    'No messages yet.',
]
for t in html_texts:
    c = c.replace(f'>{t}<', f'>{{% trans "{t}" %}}<')

for t in ['Type a message...', 'Demand amount']:
    c = c.replace(f'placeholder="{t}"', f'placeholder="{{% trans "{t}" %}}"')

write(p, c)

# ============================================================
# game_init.html — carefully
# ============================================================
p = f'{BASE}/game/game_init.html'
c = read(p)
c = add_i18n(c)

html_texts = [
    'Game Setup',
    'Initialize Game',
    'Game Configuration',
    'Number of Rounds',
    'Order Delay',
    'Shipping Delay',
    'Initial Inventory',
    'Holding Cost',
    'Backorder Cost',
    'Demand Pattern',
    'Customer Demand',
    'Save Settings',
    'Start Game',
    'Cancel',
    'Back',
    'Advanced Settings',
    'Player Setup',
    'Assign Roles',
    'Retailer',
    'Wholesaler',
    'Distributor',
    'Factory',
    'Include Customer Role',
]
for t in html_texts:
    c = c.replace(f'>{t}<', f'>{{% trans "{t}" %}}<')

write(p, c)

print("Done fixing large templates")
