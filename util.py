import connection


def get_next_id(csv_file):
    return len(connection.csv_opening(csv_file)) + 1
