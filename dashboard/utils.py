import psycopg2

db_params = {
    'dbname': 'hackbu24',
    'user': 'postgres',
    'password': 'root',
    'host': 'localhost',
    'port': '5432'
}

def connect_to_db():
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except psycopg2.Error as e:
        # logging.error("Error while establishing a database connection:", e)
        # print("Error while establishing a database connection:", e)
        return None

def run_query(query, values=[]):
    connection = connect_to_db()
    if connection is None:
        return None
    cursor = connection.cursor()
    cursor.execute(query,values)
    data = cursor.fetchall()
    # Close the database connection
    cursor.close()
    connection.close()
    return data


def get_athletes():
    athletes = run_query("SELECT distinct person FROM athlete")
    if athletes is None:
        return ["athlete1", "athlete2", "athlete3"]
    else:
        athletes = [a[0] for a in athletes]
    return athletes

def get_attempts(athlete):
    attempts = run_query(f"SELECT distinct attempt FROM athlete WHERE person = '{athlete}'")
    if attempts is None:
        return [1, 2, 3]
    else:
        attempts = [int(a[0]) for a in attempts]
    return attempts
