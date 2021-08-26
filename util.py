import connection
from datetime import datetime


def get_next_id(csv_file):
    return len(connection.csv_opening(csv_file)) + 1


def current_date():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
