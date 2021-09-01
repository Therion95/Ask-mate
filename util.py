import csv_connection
from datetime import datetime

import db_connection


def get_next_id(csv_file):
    return len(csv_connection.csv_opening(csv_file)) + 1


def current_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def query_builder(query_type, db_table, selector=None, col_to_update=None, update=None, condition=None,
                  cols_to_update=None):
    parts = [{'selecting': "SELECT", 'from': "FROM", 'updating': "UPDATE", 'inserting': "INSERT INTO", 'deleting': "DELETE",
                    'values': "VALUES", 'set': "SET", 'ret': "RETURNING"},
                   {'answers': "answer", 'questions': "question", 'comments': "comment", 'question_tags':
                       "question_tag", 'tags': "tag"},
                   {'where_con': "WHERE", 'like_con': "LIKE"},
                   {'add': "+", 'subtract': "-", 'string_con': ['%s']}]

    if query_type == "SELECT":
        if condition:
            query = f"""{parts[0]['selecting']} {selector} {parts[0]['from']} {db_table} 
            {parts[0]['where_con']} {condition};"""
        else:
            query = f"{parts[0]['selecting']} {selector} {parts[0]['from']} {db_table};"

        return query

    if query_type == "INSERT":
        columns = db_connection.column_names(db_table)
        query = f"""{parts[0]['inserting']} {db_table} ({', '.join(columns)}) {parts[0]['values']} 
        ({', '.join(len(columns) * parts[3]['string_con'])}) {parts[0]['ret']} id;"""

        return query

    if query_type == "VOTING":
        if db_table == 'answer':
            query = f"""{parts[0]['updating']} {db_table} {parts[0]['set']} {col_to_update} = {col_to_update} {update} 
            {parts[2]['where_con']} {condition} {parts[0]['ret']} question_id;"""
        else:
            query = f"""{parts[0]['updating']} {db_table} {parts[0]['set']} {col_to_update} = {col_to_update} {update} 
            {parts[2]['where_con']} {condition};"""

            f'''UPDATE nazwa kolumny SET vote_number = vote_number - 1 WHERE id = 6'''

        return query

    if query_type == "EDITING":
        if db_table == 'answer':
            query = f"""{parts[0]['updating']} {db_table} {parts[0]['set']} {cols_to_update} = ({', '.join(len(cols_to_update) * parts[3]['string_con'])})
            {parts[2]['where_con']} {condition} {parts[0]['ret']} question_id;"""
        else:
            query = f"""{parts[0]['updating']} {db_table} {parts[0]['set']} {cols_to_update} = ({', '.join(len(cols_to_update) * parts[3]['string_con'])}) 
            {parts[2]['where_con']} {condition};"""

        return query

    if query_type == 'DELETE':
        if db_table == 'answer':
            query = f"""{parts[0]['deleting']} {parts[0]['from']} {db_table} {parts[2]['where_con']} {condition}
            {parts[0]['ret']} question_id;"""

        else:
            query = f"{parts[0]['deleting']} {parts[0]['from']} {db_table} {parts[2]['where_con']} {condition};"

        return query
