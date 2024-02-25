import sqlite3 as sq

with sq.connect("db.sqlite") as con:

    print(con)

