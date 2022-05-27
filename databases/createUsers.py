# Create users table in db.sqlite

import sqlite3

conn = sqlite3.connect("databases/users.sqlite")

cursor = conn.cursor()

sql_query = """ CREATE TABLE users (
    id integer PRIMARY KEY AUTOINCREMENT,
    username text NOT NULL,
    password text NOT NULL,
    balance integer   
)"""

cursor.execute(sql_query)
cursor.close()
conn.close()

del cursor, conn