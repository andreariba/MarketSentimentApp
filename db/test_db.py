import psycopg2

try:
    connection = psycopg2.connect(
        user="postgres",
        password="example",
        host="localhost",
        port="5432",
        database="sentimentapp"
    )
    cursor = connection.cursor()

    tables = cursor.execute("SELECT * FROM information_schema.tables;")
    tables = cursor.fetchall()
    print(tables)

    print("Successfully connected to the PostgreSQL database")

    
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
