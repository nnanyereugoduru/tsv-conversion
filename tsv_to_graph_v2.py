import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import ast
import json
import os

path = r'C:\Projects\FOLDER 2\PY2\count.json'

def save():
    global COUNT
    COUNT += 1
    with open(path, 'w') as file:
        json.dump(COUNT, file, indent=4)
    print("saved")

if os.path.exists(path):
        with open(path, 'r') as file:
            COUNT = json.load(file)
else:
        COUNT = 1
        with open(path, 'w' ) as file:
            json.dump(COUNT, file, indent=4)

def parameters():
    select_feature = "Trunk1, Trunk2, Trunk3, Trunk4, time"
    tsv_file = f"C:\Projects\FOLDER 2\PY2\level1_{COUNT:04d}.tsv"
    csv_file = f"C:\Projects\FOLDER 2\PY2\level1_{COUNT:04d}.csv"
    db_file = f"C:\Projects\FOLDER 2\PY2\level1_0001.db"
    return  select_feature, tsv_file, csv_file, db_file

def read_header(tsv_file):
    meta = {}
    with open(tsv_file) as f:
        for _ in range(10):
            parts = f.readline().rstrip("\n").split("\t")
            meta[parts[0]] = parts[1:]
    return meta

def tsv_to_csv(tsv_file, csv_file):
    meta = read_header(tsv_file)
    marker_names = meta["MARKER_NAMES"]

    df = pd.read_csv(tsv_file, sep="\t", header=None, skiprows=10)
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.interpolate(limit_direction="both")

    grouped = {}
    for i, name in enumerate(marker_names):
        cols = df.columns[i * 3 : i * 3 + 3]
        grouped[name] = list(df[cols].itertuples(index=False, name=None))

    pd.DataFrame(grouped).to_csv(csv_file, index=False)

def csv_to_db(csv_file, db_file):
     conn = sqlite3.connect(rf"{db_file}")
     df = pd.read_csv(rf"{csv_file}")
     df["time"] = df.index /100.0
     df.to_sql(f"my_table{COUNT}", conn, if_exists="replace", index=False)
     conn.commit()
     conn.close()


def get_graph(db_file, select_feature):
    db = db_file
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute(f" SELECT {select_feature} FROM my_table{COUNT}")
    rows = cursor.fetchall()

    Trunk1, Trunk2, Trunk3, Trunk4, time  = zip(*rows) #this will now give me (x,y,z) for each except time
    Trunk1_x = [ast.literal_eval(v)[0] for v in Trunk1]
    Trunk2_x = [ast.literal_eval(v)[0] for v in Trunk2]
    Trunk3_x = [ast.literal_eval(v)[0] for v in Trunk3] # these sets of code take the string tuple and parses it 
    Trunk4_x = [ast.literal_eval(v)[0] for v in Trunk4]
    
    Trunk1_y = [ast.literal_eval(v)[1] for v in Trunk1]
    Trunk2_y = [ast.literal_eval(v)[1] for v in Trunk2]
    Trunk3_y = [ast.literal_eval(v)[1] for v in Trunk3]
    Trunk4_y = [ast.literal_eval(v)[1] for v in Trunk4]
    
    Trunk1_z = [ast.literal_eval(v)[2] for v in Trunk1]
    Trunk2_z = [ast.literal_eval(v)[2] for v in Trunk2]
    Trunk3_z = [ast.literal_eval(v)[2] for v in Trunk3]
    Trunk4_z = [ast.literal_eval(v)[2] for v in Trunk4]
    
    plt.plot(time,Trunk1_x, label="Trunk1_x")
    plt.plot(time,Trunk2_x, label="Trunk2_x")
    plt.plot(time,Trunk3_x, label="Trunk3_x")
    plt.plot(time,Trunk4_x, label="Trunk4_x")
    plt.xlabel('time')
    plt.ylabel('movement')
    plt.legend()
    plt.grid()
    plt.show()


def main():
    select_feature, tsv_file, csv_file, db_file = parameters()
    print(f"{COUNT} {tsv_file} {csv_file} {db_file}")
    tsv_to_csv(tsv_file,csv_file)
    csv_to_db(csv_file,db_file)
    get_graph(db_file, select_feature)
    save()


if __name__ == "__main__":
    main()

