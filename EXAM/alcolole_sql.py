import pandas as pd
from sqlalchemy import create_engine, text

# Paths
database_path= 'sqlite:///student_alcohol_intake.db'
dataset_path= '/data/datasets/prog5/SQL_example.csv'

# Function to create tables using direct SQL statements
def create_tables(connection):
    with connection.begin():
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY,
                school TEXT,
                sex TEXT,
                age INTEGER,
                address TEXT,
                famsize TEXT,
                Pstatus TEXT
            )
        """))
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS parents (
                student_id INTEGER PRIMARY KEY,
                Medu INTEGER,
                Fedu INTEGER,
                Mjob TEXT,
                Fjob TEXT,
                reason TEXT,
                guardian TEXT,
                FOREIGN KEY(student_id) REFERENCES students(student_id)
            )
        """))
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS academic_profile (
                student_id INTEGER PRIMARY KEY,
                traveltime INTEGER,
                studytime INTEGER,
                failures INTEGER,
                G1 INTEGER,
                G2 INTEGER,
                G3 INTEGER,
                FOREIGN KEY(student_id) REFERENCES students(student_id)
            )
        """))
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS lifestyle (
                student_id INTEGER PRIMARY KEY,
                higher BOOLEAN,
                internet BOOLEAN,
                romantic BOOLEAN,
                famrel INTEGER,
                freetime INTEGER,
                goout INTEGER,
                Dalc INTEGER,
                Walc INTEGER,
                health INTEGER,
                absences INTEGER,
                FOREIGN KEY(student_id) REFERENCES students(student_id)
            )
        """))
    print("2. Tables (students, parents, academic_profile, lifestyle) created successfully.")

# Function to insert data using direct SQL statements
def insert_data(connection, data):
    with connection.begin():
        for idx, row in data.iterrows():
            student_id = idx + 1
            connection.execute(text("""
                INSERT INTO students (student_id, school, sex, age, address, famsize, Pstatus)
                VALUES (:student_id, :school, :sex, :age, :address, :famsize, :Pstatus)
            """), {
                'student_id': student_id,
                'school': row['school'],
                'sex': row['sex'],
                'age': row['age'],
                'address': row['address'],
                'famsize': row['famsize'],
                'Pstatus': row['Pstatus']
            })
            connection.execute(text("""
                INSERT INTO parents (student_id, Medu, Fedu, Mjob, Fjob, reason, guardian)
                VALUES (:student_id, :Medu, :Fedu, :Mjob, :Fjob, :reason, :guardian)
            """), {
                'student_id': student_id,
                'Medu': row['Medu'],
                'Fedu': row['Fedu'],
                'Mjob': row['Mjob'],
                'Fjob': row['Fjob'],
                'reason': row['reason'],
                'guardian': row['guardian']
            })
            connection.execute(text("""
                INSERT INTO academic_profile (student_id, traveltime, studytime, failures, G1, G2, G3)
                VALUES (:student_id, :traveltime, :studytime, :failures, :G1, :G2, :G3)
            """), {
                'student_id': student_id,
                'traveltime': row['traveltime'],
                'studytime': row['studytime'],
                'failures': row['failures'],
                'G1': row['G1'],
                'G2': row['G2'],
                'G3': row['G3']
            })
            connection.execute(text("""
                INSERT INTO lifestyle (student_id, higher, internet, romantic, famrel, freetime, goout, Dalc, Walc, health, absences)
                VALUES (:student_id, :higher, :internet, :romantic, :famrel, :freetime, :goout, :Dalc, :Walc, :health, :absences)
            """), {
                'student_id': student_id,
                # Convert higher, internet, romantic column's type to BOOLEAN
                'higher': row['higher'] == 'yes',
                'internet': row['internet'] == 'yes',
                'romantic': row['romantic'] == 'yes',
                'famrel': row['famrel'],
                'freetime': row['freetime'],
                'goout': row['goout'],
                'Dalc': row['Dalc'],
                'Walc': row['Walc'],
                'health': row['health'],
                'absences': row['absences']
            })
    print("3. Data inserted successfully.")


# Function to query max alcohol consumption
def find_max_alcohol_consumption(connection):
    result = connection.execute(text("""
        SELECT MAX(Dalc) AS max_dalc, MAX(Walc) AS max_walc FROM lifestyle
    """)).fetchone()
    max_dalc = result[0]
    max_walc = result[1]
    if max_dalc > max_walc:
        print(f"4. The maximum alcohol consumption is during the week with a value of {max_dalc}.")
    else:
        print(f"4. The maximum alcohol consumption is during the weekend with a value of {max_walc}.")


# Function to remove privacy-sensitive columns
def remove_sensitive_data(connection):
    """Remove the 'school' and 'address' columns from the 'students' table."""
    connection.execute(text("ALTER TABLE students DROP COLUMN school"))
    connection.execute(text("ALTER TABLE students DROP COLUMN address"))
    print("5. Privacy-sensitive columns 'school' and 'address' removed.")

# Function to drop tables 
def drop_all_tables(connection):
    """Drop each table in the database by name if it exists."""
    with connection.begin():
        connection.execute(text("DROP TABLE IF EXISTS lifestyle"))
        connection.execute(text("DROP TABLE IF EXISTS academic_profile"))
        connection.execute(text("DROP TABLE IF EXISTS parents"))
        connection.execute(text("DROP TABLE IF EXISTS students"))
    print("All tables dropped successfully.")


def main():
    # Connect to the SQLite database
    engine = create_engine(database_path)
    connection = engine.connect()
    print("Database connection established.")

    data = pd.read_csv(dataset_path)
    print("1. Data loaded successfully.")

    # To avoid any problem to run again
    drop_all_tables(connection)

    create_tables(connection)
    insert_data(connection, data)
    find_max_alcohol_consumption(connection)
    remove_sensitive_data(connection)


    # Close connection
    connection.close()
    print("Database connection closed.")

if __name__ == "__main__":
    main()
