import os

import psycopg2
import psycopg2.extras


def connect_to_db():
    user_name, password, host, database_name = \
        os.environ.get('PSQL_USER_NAME'), os.environ.get('PSQL_PASSWORD'), \
        os.environ.get('PSQL_HOST'), os.environ.get('PSQL_DB_NAME')

    return psycopg2.connect(dbname=database_name, user=user_name, password=password, host=host)


def creating_a_cursor(connection):
    return connection.cursor()


def creating_a_dict_cursor(connection):
    return connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def executor(func):
    def decorator(*args, **kwargs):
        connection = connect_to_db()
        connection.autocommit = True
        dict_cursor = creating_a_dict_cursor(connection)
        to_return = func(dict_cursor, *args, **kwargs)
        dict_cursor.close()
        connection.close()

        return to_return

    return decorator


@executor
def column_names(cursor, db_table):
    cursor.execute(f"Select * FROM {db_table} LIMIT 0")

    return [desc[0] for desc in cursor.description][1:]
