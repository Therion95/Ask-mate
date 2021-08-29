import csv_connection
from datetime import datetime


def get_next_id(csv_file):
    return len(csv_connection.csv_opening(csv_file)) + 1


def current_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
