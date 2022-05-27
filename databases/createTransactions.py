# Create transactions table in db.sqlite

import sqlite3

conn = sqlite3.connect("databases/db.sqlite")

cursor = conn.cursor()

# datetime stored in the format - 'YYYY-MM-DD HH:MM:SS'
sql_query = """ CREATE TABLE transactions (
    id integer PRIMARY KEY AUTOINCREMENT,
    datetime text,
    sender integer,
    receiver integer,
    amount integer   
)"""

cursor.execute(sql_query)
cursor.close()
conn.close()

del cursor, conn