import re
import sys
import pymysql

conn = pymysql.connect(
    host='localhost', user='root', password='wang97976',
    database='key_person_mgmt', charset='utf8mb4'
)

sql_file = sys.argv[1] if len(sys.argv) > 1 else None
if not sql_file:
    print('Usage: run_migration.py <sql_file>')
    sys.exit(1)

with open(sql_file, 'r', encoding='utf-8') as f:
    raw = f.read()

raw = re.sub(r'--[^\n]*', '', raw)
raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)

cursor = conn.cursor()
for statement in raw.split(';'):
    s = statement.strip()
    if s:
        try:
            cursor.execute(s)
            print(f'OK: {s[:70]}...')
        except Exception as e:
            print(f'ERR: {s[:70]}... -> {e}')

conn.commit()
cursor.close()
conn.close()
print('Migration complete!')
