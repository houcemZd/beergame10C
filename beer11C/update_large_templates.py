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

def bulk_replace(content, pairs):
    for old, new in pairs:
        content = content.replace(old, new)
    return content

# ============================================================
# lobby.html
# ============================================================
p = f'{BASE}/game/lobby.html'
c = read(p)
c = add_i18n(c)

pairs = [
    ('Game Lobby', '{% trans "Game Lobby" %}'),
    ('Waiting for players...', '{% trans "Waiting for players..." %}'),
    ('Start Game', '{% trans "Start Game" %}'),
    ('Leave Game', '{% trans "Leave Game" %}'),
    ('Copy Link', '{% trans "Copy Link" %}'),
    ('Copied!', '{% trans "Copied!" %}'),
    ('Players', '{% trans "Players" %}'),
    ('Chat', '{% trans "Chat" %}'),
    ('Send', '{% trans "Send" %}'),
    ('Game Settings', '{% trans "Game Settings" %}'),
    ('Rounds:', '{% trans "Rounds:" %}'),
    ('Delay:', '{% trans "Delay:" %}'),
    ('Inventory:', '{% trans "Inventory:" %}'),
    ('Status:', '{% trans "Status:" %}'),
    ('>Waiting<', '>{% trans "Waiting" %}<'),
    ('>Ready<', '>{% trans "Ready" %}<'),
    ('Join Link', '{% trans "Join Link" %}'),
    ('Share this link', '{% trans "Share this link" %}'),
    ('Type a message...', '{% trans "Type a message..." %}'),
    ('No messages yet.', '{% trans "No messages yet." %}'),
    ('Waiting for the game to start...', '{% trans "Waiting for the game to start..." %}'),
    ('Game will start shortly...', '{% trans "Game will start shortly..." %}'),
]
c = bulk_replace(c, pairs)
write(p, c)

# ============================================================
# play.html
# ============================================================
p = f'{BASE}/game/play.html'
c = read(p)
c = add_i18n(c)

pairs = [
    ('Your Inventory', '{% trans "Your Inventory" %}'),
    ('Incoming Order', '{% trans "Incoming Order" %}'),
    ('Incoming Shipment', '{% trans "Incoming Shipment" %}'),
    ('Your Order', '{% trans "Your Order" %}'),
    ('Place Order', '{% trans "Place Order" %}'),
    ('Submit Order', '{% trans "Submit Order" %}'),
    ('Current Round', '{% trans "Current Round" %}'),
    ('Round', '{% trans "Round" %}'),
    ('Inventory:', '{% trans "Inventory:" %}'),
    ('Backorder:', '{% trans "Backorder:" %}'),
    ('Cost:', '{% trans "Cost:" %}'),
    ('Total Cost:', '{% trans "Total Cost:" %}'),
    ('units', '{% trans "units" %}'),
    ('Waiting for other players...', '{% trans "Waiting for other players..." %}'),
    ('Game Over', '{% trans "Game Over" %}'),
    ('View Results', '{% trans "View Results" %}'),
    ('Supply Chain Status', '{% trans "Supply Chain Status" %}'),
    ('History', '{% trans "History" %}'),
    ('Order History', '{% trans "Order History" %}'),
    ('Inventory History', '{% trans "Inventory History" %}'),
    ('Retailer', '{% trans "Retailer" %}'),
    ('Wholesaler', '{% trans "Wholesaler" %}'),
    ('Distributor', '{% trans "Distributor" %}'),
    ('Factory', '{% trans "Factory" %}'),
    ('Customer', '{% trans "Customer" %}'),
    ('Chat', '{% trans "Chat" %}'),
    ('Send', '{% trans "Send" %}'),
    ('Type a message...', '{% trans "Type a message..." %}'),
    ('You have', '{% trans "You have" %}'),
    ('units in stock', '{% trans "units in stock" %}'),
    ('units on backorder', '{% trans "units on backorder" %}'),
    ('has ordered', '{% trans "has ordered" %}'),
    ('shipment of', '{% trans "shipment of" %}'),
    ('Pipeline:', '{% trans "Pipeline:" %}'),
    ('weeks', '{% trans "weeks" %}'),
    ('Holding Cost', '{% trans "Holding Cost" %}'),
    ('Backorder Cost', '{% trans "Backorder Cost" %}'),
    ('week', '{% trans "week" %}'),
    ('Order amount', '{% trans "Order amount" %}'),
    ('Demand this round:', '{% trans "Demand this round:" %}'),
    ('Production order', '{% trans "Production order" %}'),
]
c = bulk_replace(c, pairs)
write(p, c)

# ============================================================
# results.html
# ============================================================
p = f'{BASE}/game/results.html'
c = read(p)
c = add_i18n(c)

pairs = [
    ('Game Results', '{% trans "Game Results" %}'),
    ('Results', '{% trans "Results" %}'),
    ('Total Cost', '{% trans "Total Cost" %}'),
    ('Holding Cost', '{% trans "Holding Cost" %}'),
    ('Backorder Cost', '{% trans "Backorder Cost" %}'),
    ('Inventory History', '{% trans "Inventory History" %}'),
    ('Order History', '{% trans "Order History" %}'),
    ('Demand History', '{% trans "Demand History" %}'),
    ('Bullwhip Effect', '{% trans "Bullwhip Effect" %}'),
    ('Bullwhip Ratio', '{% trans "Bullwhip Ratio" %}'),
    ('Download CSV', '{% trans "Download CSV" %}'),
    ('Back to Sessions', '{% trans "Back to Sessions" %}'),
    ('Play Again', '{% trans "Play Again" %}'),
    ('Round', '{% trans "Round" %}'),
    ('Player', '{% trans "Player" %}'),
    ('Role', '{% trans "Role" %}'),
    ('Retailer', '{% trans "Retailer" %}'),
    ('Wholesaler', '{% trans "Wholesaler" %}'),
    ('Distributor', '{% trans "Distributor" %}'),
    ('Factory', '{% trans "Factory" %}'),
    ('Customer', '{% trans "Customer" %}'),
    ('Cost per Round', '{% trans "Cost per Round" %}'),
    ('Cumulative Cost', '{% trans "Cumulative Cost" %}'),
    ('Supply Chain Analysis', '{% trans "Supply Chain Analysis" %}'),
    ('Period', '{% trans "Period" %}'),
    ('Score', '{% trans "Score" %}'),
    ('Performance', '{% trans "Performance" %}'),
    ('weeks', '{% trans "weeks" %}'),
    ('units', '{% trans "units" %}'),
    ('Game Summary', '{% trans "Game Summary" %}'),
    ('Duration', '{% trans "Duration" %}'),
    ('Players', '{% trans "Players" %}'),
    ('Total Rounds', '{% trans "Total Rounds" %}'),
    ('Winner', '{% trans "Winner" %}'),
    ('Best Player', '{% trans "Best Player" %}'),
]
c = bulk_replace(c, pairs)
write(p, c)

# ============================================================
# customer_play.html
# ============================================================
p = f'{BASE}/game/customer_play.html'
c = read(p)
c = add_i18n(c)

pairs = [
    ('Customer Dashboard', '{% trans "Customer Dashboard" %}'),
    ('Place Demand', '{% trans "Place Demand" %}'),
    ('Submit Demand', '{% trans "Submit Demand" %}'),
    ('Demand this round:', '{% trans "Demand this round:" %}'),
    ('Current Round', '{% trans "Current Round" %}'),
    ('Round', '{% trans "Round" %}'),
    ('Waiting for other players...', '{% trans "Waiting for other players..." %}'),
    ('Game Over', '{% trans "Game Over" %}'),
    ('View Results', '{% trans "View Results" %}'),
    ('Demand History', '{% trans "Demand History" %}'),
    ('Chat', '{% trans "Chat" %}'),
    ('Send', '{% trans "Send" %}'),
    ('Type a message...', '{% trans "Type a message..." %}'),
    ('Demand amount', '{% trans "Demand amount" %}'),
    ('units', '{% trans "units" %}'),
    ('Customer', '{% trans "Customer" %}'),
]
c = bulk_replace(c, pairs)
write(p, c)

# ============================================================
# game_init.html
# ============================================================
p = f'{BASE}/game/game_init.html'
c = read(p)
c = add_i18n(c)

pairs = [
    ('Game Setup', '{% trans "Game Setup" %}'),
    ('Initialize Game', '{% trans "Initialize Game" %}'),
    ('Game Configuration', '{% trans "Game Configuration" %}'),
    ('Number of Rounds', '{% trans "Number of Rounds" %}'),
    ('Order Delay', '{% trans "Order Delay" %}'),
    ('Shipping Delay', '{% trans "Shipping Delay" %}'),
    ('Initial Inventory', '{% trans "Initial Inventory" %}'),
    ('Holding Cost', '{% trans "Holding Cost" %}'),
    ('Backorder Cost', '{% trans "Backorder Cost" %}'),
    ('Demand Pattern', '{% trans "Demand Pattern" %}'),
    ('Customer Demand', '{% trans "Customer Demand" %}'),
    ('Save Settings', '{% trans "Save Settings" %}'),
    ('Start Game', '{% trans "Start Game" %}'),
    ('Cancel', '{% trans "Cancel" %}'),
    ('Back', '{% trans "Back" %}'),
    ('Advanced Settings', '{% trans "Advanced Settings" %}'),
    ('weeks', '{% trans "weeks" %}'),
    ('units', '{% trans "units" %}'),
    ('Player Setup', '{% trans "Player Setup" %}'),
    ('Assign Roles', '{% trans "Assign Roles" %}'),
    ('Retailer', '{% trans "Retailer" %}'),
    ('Wholesaler', '{% trans "Wholesaler" %}'),
    ('Distributor', '{% trans "Distributor" %}'),
    ('Factory', '{% trans "Factory" %}'),
    ('Include Customer Role', '{% trans "Include Customer Role" %}'),
]
c = bulk_replace(c, pairs)
write(p, c)

print("Done with large templates")
