import csv_connection
from flask import session
import bcrypt
from datetime import datetime


def get_next_id(csv_file):
    return len(csv_connection.csv_opening(csv_file)) + 1


def current_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf8'), hashed.encode('utf-8'))


def is_logged_in():
    if 'user' in session.keys():
        return True
    else:
        return False


def get_user_id_from_session():
    if 'user' in session.keys():
        return session['user']['id']
    else:
        raise RuntimeError('Not logged in user')

#
# def query_builder(query_type, db_table, selector=None, col_to_update=None, update=None, condition=None, order=None,
#                   limit=None, cols_to_update=None, ret=None):
#     parts = [{'selecting': "SELECT", 'from': "FROM", 'updating': "UPDATE", 'inserting': "INSERT INTO", 'deleting': "DELETE",
#                     'values': "VALUES", 'set': "SET", 'ret': "RETURNING"},
#                    {'answers': "answer", 'questions': "question", 'comments': "comment", 'question_tags':
#                        "question_tag", 'tags': "tag"},
#                    {'where_con': "WHERE", 'like_con': "LIKE", 'order': "ORDER BY", 'limit': "LIMIT"},
#                    {'add': "+", 'subtract': "-", 'string_con': ['%s']}]
#
#     if query_type == "SELECT":
#         if condition:
#             query = f"""{parts[0]['selecting']} {selector} {parts[0]['from']} {db_table}
#             {parts[2]['where_con']} {condition};"""
#         elif order:
#             query = f"""{parts[0]['selecting']} {selector} {parts[0]['from']} {db_table}
#             {parts[2]['order']} {order};"""
#             if limit:
#                 query = f"""{parts[0]['selecting']} {selector} {parts[0]['from']} {db_table}
#                 {parts[2]['order']} {order} {parts[2]['limit']} {limit};"""
#         elif limit:
#             query = f"""{parts[0]['selecting']} {selector} {parts[0]['from']} {db_table}
#             {parts[2]['limit']} {limit};"""
#             print(order)
#             if order:
#                 query = f"""{parts[0]['selecting']} {selector} {parts[0]['from']} {db_table}
#                 {parts[2]['order']} {order} {parts[2]['limit']} {limit};"""
#         else:
#             query = f"{parts[0]['selecting']} {selector} {parts[0]['from']} {db_table};"
#
#         return query
#
#     if query_type == "INSERT":
#         columns = db_data_manager.get_listed_column_names(db_table)
#         if len(columns) == 1:
#             query = f"""{parts[0]['inserting']} {db_table} ({', '.join(columns)}) {parts[0]['values']}
#             ({', '.join(len(columns) * parts[3]['string_con'])}) {parts[0]['ret']} id;"""
#         else:
#             query = f"""{parts[0]['inserting']} {db_table} ({', '.join(columns)}) {parts[0]['values']}
#             ({', '.join(len(columns) * parts[3]['string_con'])}) {parts[0]['ret']} id;"""
#
#         return query
#
#     if query_type == "VOTING":
#         if db_table == 'answer':
#             query = f"""{parts[0]['updating']} {db_table} {parts[0]['set']} {col_to_update} = {col_to_update} {update}
#             {parts[2]['where_con']} {condition} {parts[0]['ret']} question_id;"""
#         else:
#             query = f"""{parts[0]['updating']} {db_table} {parts[0]['set']} {col_to_update} = {col_to_update} {update}
#             {parts[2]['where_con']} {condition};"""
#
#         return query
#
#     if query_type == "EDITING":
#         if db_table == 'answer':
#             if len(cols_to_update) > 1:
#                 query = f"""{parts[0]['updating']} {db_table} {parts[0]['set']} ({', '.join(cols_to_update)}) = ({', '.join(len(cols_to_update) * parts[3]['string_con'])})
#                 {parts[2]['where_con']} {condition} {parts[0]['ret']} question_id;"""
#             else:
#                 query = f"""{parts[0]['updating']} {db_table} {parts[0]['set']} {', '.join(cols_to_update)} = {', '.join(len(cols_to_update) * parts[3]['string_con'])}
#                 {parts[2]['where_con']} {condition} {parts[0]['ret']} question_id;"""
#         else:
#             if len(cols_to_update) > 1:
#                 query = f"""{parts[0]['updating']} {db_table} {parts[0]['set']} ({', '.join(cols_to_update)}) = ({', '.join(len(cols_to_update) * parts[3]['string_con'])})
#                 {parts[2]['where_con']} {condition};"""
#             else:
#                 query = f"""{parts[0]['updating']} {db_table} {parts[0]['set']} {', '.join(cols_to_update)} = {', '.join(len(cols_to_update) * parts[3]['string_con'])}
#                 {parts[2]['where_con']} {condition};"""
#
#         return query
#
#     if query_type == 'DELETE':
#         if db_table == 'answer':
#             query = f"""{parts[0]['deleting']} {parts[0]['from']} {db_table} {parts[2]['where_con']} {condition}
#             {parts[0]['ret']} question_id;"""
#         elif db_table == 'comment':
#
#             query = f"""{parts[0]['deleting']} {parts[0]['from']} {db_table} {parts[2]['where_con']} {condition}
#             {parts[0]['ret']} question_id;"""
#
#         else:
#             query = f"{parts[0]['deleting']} {parts[0]['from']} {db_table} {parts[2]['where_con']} {condition};"
#
#         return query
