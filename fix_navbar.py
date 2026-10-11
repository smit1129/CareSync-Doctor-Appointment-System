import re

filepath = 'frontend/src/components/Navbar.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    (r'\btext-white/90\b', 'text-primary-foreground/90'),
    (r'\bhover:text-white\b', 'hover:text-primary-foreground'),
    (r'\btext-white\b', 'text-primary-foreground'),
    (r'\bbg-white/10\b', 'bg-primary-foreground/10'),
    (r'\bbg-white text-teal-700\b', 'bg-primary-foreground text-primary'),
    (r'\bbg-teal-700/95\b', 'bg-primary/95'),
    (r'\btext-white/80\b', 'text-primary-foreground/80'),
    (r'\btext-white/70\b', 'text-primary-foreground/70'),
    (r'\bhover:bg-teal-50\b', 'hover:bg-primary-foreground/90'),
    (r'\bborder-white/10\b', 'border-primary-foreground/10'),
]

for pattern, repl in replacements:
    content = re.sub(pattern, repl, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated Navbar.tsx")
