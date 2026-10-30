import sqlite3

def build_database(db_path, tables):
    """Write a dict of {table_name: DataFrame} to a SQLite database, replacing existing tables."""
    con = sqlite3.connect(db_path)
    try:
        for name, df in tables.items():
            df.to_sql(name, con, if_exists = 'replace', index = False)
    finally:
        con.close()