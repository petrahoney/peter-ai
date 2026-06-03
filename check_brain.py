lines = open(
    'C:\\peter-ai\\core\\brain.py',
    encoding='utf-8', errors='replace'
).readlines()

for i, l in enumerate(lines, 1):
    if ('user_name' in l.lower() and
        'USER_NAME' not in l and
        'def ' not in l):
        print(f'{i}: {l.rstrip()[:100]}')