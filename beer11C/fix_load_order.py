"""Fix {% load i18n %} placement - must come after {% extends %} tag."""
import os, re

TDIR = '/home/runner/work/beergameenib.github.io/beergameenib.github.io/beer11C/game/templates'

for root, dirs, files in os.walk(TDIR):
    for fname in files:
        if not fname.endswith('.html'):
            continue
        path = os.path.join(root, fname)
        with open(path, encoding='utf-8') as f:
            content = f.read()
        
        if '{% load i18n %}' not in content:
            continue
        if '{% extends' not in content:
            continue
        
        # Check if load i18n comes before extends (the problem case)
        load_pos = content.find('{% load i18n %}')
        ext_pos = content.find('{% extends')
        
        if load_pos < ext_pos:
            # Remove load i18n from current position
            content = content.replace('{% load i18n %}\n', '', 1)
            # Find the extends line end and insert load i18n after it
            ext_line_end = content.find('\n', content.find('{% extends')) + 1
            content = content[:ext_line_end] + '{% load i18n %}\n' + content[ext_line_end:]
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed load order: {path}")

print("Done fixing load order")
