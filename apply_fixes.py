import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content

    # 1. Page backgrounds
    new_content = new_content.replace('bg-surface hover:brightness-95 dark:hover:brightness-110 py-8', 'bg-background py-8')
    new_content = new_content.replace('bg-surface hover:brightness-95 dark:hover:brightness-110"', 'bg-background"')
    
    # Static container replacements (any remaining ones that shouldn't have hover, except table rows which are tr hover:bg-surface)
    # The string is "bg-surface hover:brightness-95 dark:hover:brightness-110"
    # Let's replace it with "bg-surface" if it's on a div that isn't supposed to be interactive.
    # We can replace 'bg-surface hover:brightness-95 dark:hover:brightness-110' with 'bg-surface' in general, 
    # except when it's prefixed by 'hover:' which would mean the hover was intentional (e.g. `hover:bg-surface hover:brightness...`)
    # Wait, in the table rows it is: `className="hover:bg-surface hover:brightness-95 dark:hover:brightness-110"`
    # For those, we can just change it to `className="hover:bg-surface dark:hover:bg-surface/80"` maybe.
    
    # First, let's replace all `hover:bg-surface hover:brightness-95 dark:hover:brightness-110` with `hover:bg-surface/80 dark:hover:bg-surface/60`
    new_content = new_content.replace('hover:bg-surface hover:brightness-95 dark:hover:brightness-110', 'hover:bg-surface/80')
    
    # Then replace the static `bg-surface hover:brightness-95 dark:hover:brightness-110` with `bg-surface`
    new_content = new_content.replace('bg-surface hover:brightness-95 dark:hover:brightness-110', 'bg-surface')
    
    # Fix `brightness-95 dark:brightness-125` (from bg-gray-100) -> `bg-surface/50` or just `bg-surface border border-border`
    new_content = new_content.replace('bg-surface brightness-95 dark:brightness-125', 'bg-surface/50')
    new_content = new_content.replace('bg-surface brightness-90 dark:brightness-150', 'bg-surface/30')

    # 2. Redundant text-white
    new_content = new_content.replace('bg-primary text-primary-foreground rounded-full flex items-center justify-center text-white', 'bg-primary text-primary-foreground rounded-full flex items-center justify-center')
    new_content = new_content.replace('bg-primary text-primary-foreground rounded-xl flex items-center justify-center text-white', 'bg-primary text-primary-foreground rounded-xl flex items-center justify-center')
    new_content = new_content.replace('bg-primary text-primary-foreground rounded-2xl flex items-center justify-center text-white', 'bg-primary text-primary-foreground rounded-2xl flex items-center justify-center')

    # 3. Notification badge text color
    new_content = new_content.replace('bg-red-500 text-primary-foreground', 'bg-red-500 text-white')

    # 4. Unselected rating-star color (in patient/dashboard/page.tsx)
    new_content = new_content.replace('text-gray-200', 'text-foreground/20')

    # 5. Make light-only teal and amber accent backgrounds readable
    new_content = new_content.replace('bg-teal-50', 'bg-teal-50 dark:bg-teal-900/30')
    new_content = new_content.replace('text-teal-700', 'text-teal-700 dark:text-teal-400')
    new_content = new_content.replace('border-teal-500', 'border-teal-500 dark:border-teal-400')
    new_content = new_content.replace('bg-amber-50', 'bg-amber-50 dark:bg-amber-900/30')
    new_content = new_content.replace('border-amber-100', 'border-amber-100 dark:border-amber-900/50')
    new_content = new_content.replace('text-amber-700', 'text-amber-700 dark:text-amber-400')
    new_content = new_content.replace('text-amber-500', 'text-amber-500 dark:text-amber-400')
    new_content = new_content.replace('bg-teal-100', 'bg-teal-100 dark:bg-teal-900/50')
    new_content = new_content.replace('text-teal-800', 'text-teal-800 dark:text-teal-300')
    # Cleanup duplicate darks if any (e.g. text-teal-700 dark:text-teal-400 dark:text-teal-400)
    new_content = new_content.replace(' dark:bg-teal-900/30 dark:bg-teal-900/30', ' dark:bg-teal-900/30')
    new_content = new_content.replace(' dark:text-teal-400 dark:text-teal-400', ' dark:text-teal-400')
    new_content = new_content.replace(' dark:border-teal-400 dark:border-teal-400', ' dark:border-teal-400')

    # 6. Hero transparent backgrounds (in page.tsx)
    if 'page.tsx' in filepath and not 'dashboard' in filepath:
        new_content = new_content.replace('bg-surface/10', 'bg-white/10')
        new_content = new_content.replace('bg-surface/5 ', 'bg-white/5 ')
        new_content = new_content.replace('bg-surface/20', 'bg-white/20')
        new_content = new_content.replace('bg-surface/30', 'bg-white/30')

    # 8. Notification dropdown border-gray-50
    new_content = new_content.replace('border-gray-50', 'border-border')

    # 9. Admin modal input border
    if 'admin\\dashboard' in filepath or 'admin/dashboard' in filepath:
        new_content = new_content.replace('className="w-full px-4 py-2 border rounded-lg', 'className="w-full px-4 py-2 border border-border rounded-lg')

    # 10. Restore registration placeholders
    if 'auth\\register' in filepath or 'auth/register' in filepath:
        new_content = new_content.replace('placeholder="your name"', 'placeholder="John Doe"')
        new_content = new_content.replace('placeholder="+91-555-0000"', 'placeholder="+1-555-0000"')

    # Write back if changed
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

for root, _, files in os.walk('frontend/src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            process_file(os.path.join(root, file))
