import os
import re

replacements = [
    (r'bg-gradient-to-r from-teal-600 to-cyan-600 text-white', 'bg-primary text-primary-foreground'),
    (r'bg-gradient-to-br from-teal-600 via-cyan-700 to-teal-800 text-white', 'bg-primary text-primary-foreground'),
    (r'bg-gradient-to-r from-teal-600 to-cyan-700 text-white', 'bg-primary text-primary-foreground'),
    (r'bg-gradient-to-br from-teal-500 to-cyan-600', 'bg-primary'),
    (r'bg-gradient-to-b from-gray-50 to-white', 'bg-surface'),
    (r'text-white', 'text-primary-foreground'),
]

def process_file(filepath):
    # Only process files that were listed in the grep output
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    # Replace gradients
    new_content = new_content.replace('bg-gradient-to-r from-teal-600 to-cyan-600 text-white', 'bg-primary text-primary-foreground')
    new_content = new_content.replace('bg-gradient-to-br from-teal-600 via-cyan-700 to-teal-800 text-white', 'bg-primary text-primary-foreground')
    new_content = new_content.replace('bg-gradient-to-r from-teal-600 to-cyan-700 text-white', 'bg-primary text-primary-foreground')
    new_content = new_content.replace('bg-gradient-to-br from-teal-500 to-cyan-600', 'bg-primary text-primary-foreground')
    new_content = new_content.replace('bg-gradient-to-b from-gray-50 to-white', 'bg-surface')
    # Some buttons have text-white after bg-gradient replacement missed it if not exactly matching, let's fix them manually via re
    new_content = re.sub(r'bg-gradient-to-[a-z]+ from-teal-\d+ (?:via-cyan-\d+ )?to-(?:cyan|teal)-\d+', 'bg-primary', new_content)

    # Some remaining 'text-white' inside bg-primary blocks
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated gradients in {filepath}")

for root, _, files in os.walk('frontend/src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            process_file(os.path.join(root, file))
