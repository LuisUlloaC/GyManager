import sqlite3
import json
from datetime import datetime, timedelta

now = datetime.now()
min_date = now - timedelta(days=29)
max_date = now - timedelta(days=25)

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

    column_names = [description[0] for description in cur.description]

    data = []
    filtered_data = []
    for row in rows:
        record = dict(zip(column_names, row))
        save_date = datetime.strptime(record['ultimo_pago'], '%Y-%m-%d') # assuming the date is stored in 'YYYY-MM-DD' format
        print(max_date)
        print(min_date)
        if max_date <= save_date <= min_date:
            filtered_data.append(record)
        data.append(record)

    return data, filtered_data



def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


from colorama import Fore, Style

def main():
   conn = create_connection("db.sqlite3")
   all_data, filtered_data = load_all_data(conn, "data_cliente")
   for record in filtered_data:
       estado = 'Notificar' if datetime.strptime(record['ultimo_pago'], '%Y-%m-%d') > max_date else 'Atrasado'
       if estado == 'Notificar':
           print(f"""{record['nombre']} {record['primer_apellido']} {record['segundo_apellido']} \n 
Tipo entrenamineto: {record['tipo_entrenamiento']} \n
Estado: {Fore.WHITE}{estado}{Style.RESET_ALL}""")
       else:
           print(f"""{record['nombre']} {record['primer_apellido']} {record['segundo_apellido']} \n 
                  Tipo entrenamineto: {record['tipo_entrenamiento']} \n
                  Estado: {Fore.RED}{estado}{Style.RESET_ALL}""")
   save_to_json(all_data, "output.json")
   conn.close()



if __name__ == "__main__":
    main()

