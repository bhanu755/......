import shutil
import sqlite3
import hashlib
import re

# Backup DB
shutil.copy('data/meetsphere.db', 'data/meetsphere.db.bak')
print('backup created: data/meetsphere.db.bak')

conn = sqlite3.connect('data/meetsphere.db')
c = conn.cursor()
rows = c.execute('SELECT username, password FROM users').fetchall()
hex_re = re.compile(r'^[0-9a-f]{64}$', re.I)
updated = 0
for u, p in rows:
    if not isinstance(p, str) or not hex_re.match(p):
        h = hashlib.sha256(p.encode('utf-8')).hexdigest()
        c.execute('UPDATE users SET password=? WHERE username=?', (h, u))
        print('hashed', u)
        updated += 1

conn.commit()
conn.close()
print('done', updated)
