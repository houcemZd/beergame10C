"""Carefully update play.html with i18n tags without breaking JS variable names."""
import re

path = '/home/runner/work/beergameenib.github.io/beergameenib.github.io/beer11C/game/templates/game/play.html'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Add {% load i18n %} at the very top
if '{% load i18n %}' not in c:
    c = '{% load i18n %}\n' + c

# Only do replacements where the string appears as visible HTML text (surrounded by > < or as attribute values)
# Use a more careful approach: only replace inside HTML tag text content / specific attributes

def html_trans(content, english, tag_context=True):
    """Replace >English< with >{% trans "English" %}<"""
    content = content.replace(f'>{english}<', f'>{{% trans "{english}" %}}<')
    return content

# Safe replacements - strings that appear as HTML text content (inside tags)
safe_html_pairs = [
    # These appear as pure text nodes in HTML (not in JS)
    ('Your Inventory', 'Votre inventaire'),
    ('Incoming Order', 'Commande reçue'),
    ('Incoming Shipment', 'Livraison reçue'),
    ('Your Order', 'Votre commande'),
    ('Place Order', 'Passer la commande'),
    ('Submit Order', 'Valider la commande'),
    ('Current Round', 'Tour actuel'),
    ('Waiting for other players...', 'En attente des autres joueurs…'),
    ('Game Over', 'Fin de partie'),
    ('View Results', 'Voir les résultats'),
    ('Supply Chain Status', 'État de la chaîne d\'approvisionnement'),
    ('Order History', 'Historique des commandes'),
    ('Inventory History', 'Historique des stocks'),
    ('Retailer', 'Détaillant'),
    ('Wholesaler', 'Grossiste'),
    ('Distributor', 'Distributeur'),
    ('Factory', 'Usine'),
    ('Customer', 'Client'),
    ('Chat', 'Chat'),
    ('Type a message...', 'Saisissez un message…'),
]

for english, _french in safe_html_pairs:
    c = c.replace(f'>{english}<', f'>{{% trans "{english}" %}}<')

# Button texts / label texts that appear in HTML attributes or button content
c = c.replace('>Send<', '>{% trans "Send" %}<')
c = c.replace('>Submit Order<', '>{% trans "Submit Order" %}<')

# Title/header patterns
c = re.sub(r'(<h[123][^>]*>)\s*Round\s*(</h[123]>)', r'\1{% trans "Round" %}\2', c)

write_str = c

with open(path, 'w', encoding='utf-8') as f:
    f.write(write_str)
print(f"Fixed play.html ({len(write_str)} bytes)")
