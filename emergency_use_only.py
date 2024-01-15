import sqlite3

def create_connection(db_file):
   conn = None
   try:
       conn = sqlite3.connect(db_file)
   except Exception as e:
       print(e)
   return conn

def load_all_data(conn, table_name):
   cur = conn.cursor()
   cur.execute(f"SELECT * FROM {table_name}")
   rows = cur.fetchall()

   for row in rows:
       print(row)

def main():
   conn = create_connection("your_database.db")
   load_all_data(conn, "your_table")
   conn.close()

if __name__ == "__main__":
   main()
