import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
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
    select_feature = "Trunk1_x, Trunk2_x, Trunk3_x, Trunk4_x, time"
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

def tsv_to_db(tsv_file, db_file):
    conn = sqlite3.connect(rf"{db_file}")
    meta = read_header(tsv_file)
    marker_names = meta["MARKER_NAMES"]
    freq = float(meta["FREQUENCY"][0])

    df = pd.read_csv(tsv_file, sep="\t", header=None, skiprows=10)
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.interpolate(limit_direction="both")

    cols = [f"{marker_name}_{cord}" for marker_name in marker_names for cord in "xyz" ]
    df = df.iloc[:, :len(cols)].copy()
    df.columns = cols
    df["time"] = df.index / freq # 100 hertz
    #pd.DataFrame(grouped).to_csv(csv_file, index=False)
    df.to_sql(f"my_table{COUNT}", conn, if_exists="replace")
    conn.commit()
    conn.close()

def get_graph(db_file, select_feature):
    db = db_file
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute(f" SELECT {select_feature} FROM my_table{COUNT}")
    rows = cursor.fetchall()
    
    a,b,c,d, t = zip(*rows)
    time = t
    
    plt.plot(time,a, label="Trunk1_x")
    plt.plot(time,b, label="Trunk2_x")
    plt.plot(time,c, label="Trunk3_x")
    plt.plot(time,d, label="Trunk4_x")
    plt.xlabel('time')
    plt.ylabel('movement')
    plt.legend()
    plt.grid()
    plt.show()


def main():
    select_feature, tsv_file, csv_file, db_file = parameters()
    #save()
    tsv_to_db(tsv_file, db_file)
    get_graph(db_file, select_feature)


if __name__ == "__main__":
    main()

