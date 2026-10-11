import os
import re

replacements = [
    (r'\bbg-white\b', 'bg-surface'),
    (r'\btext-gray-900\b', 'text-foreground'),
    (r'\btext-gray-800\b', 'text-foreground/90'),
    (r'\btext-gray-700\b', 'text-foreground/80'),
    (r'\btext-gray-600\b', 'text-foreground/70'),
    (r'\btext-gray-500\b', 'text-foreground/60'),
    (r'\bborder-gray-100\b', 'border-border'),
    (r'\bborder-gray-200\b', 'border-border'),
    (r'\bbg-gray-50\b', 'bg-surface hover:brightness-95 dark:hover:brightness-110'),
    (r'\bbg-gray-100\b', 'bg-surface brightness-95 dark:brightness-125'),
    (r'\bbg-gray-200\b', 'bg-surface brightness-90 dark:brightness-150'),
]

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for pattern, repl in replacements:
        new_content = re.sub(pattern, repl, new_content)
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

for root, _, files in os.walk('frontend/src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            process_file(os.path.join(root, file))
