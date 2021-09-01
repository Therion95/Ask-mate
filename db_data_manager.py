import os

import psycopg2
import psycopg2.extras
from psycopg2 import sql

import csv_connection
import db_connection
import files_connection
import util

# GLOBAL directory for the app config
UPLOAD_FOLDER_A = os.environ.get('UPLOAD_FOLDER_A')
UPLOAD_FOLDER_Q = os.environ.get('UPLOAD_FOLDER_Q')
# GLOBAL directories to our CSV files:
QUESTIONS = os.environ.get('QUESTIONS_PATH')
ANSWERS = os.environ.get('ANSWERS_PATH')
COMMENTS_Q = os.environ.get('COMMENTS_Q')
COMMENTS_A = os.environ.get('COMMENTS_A')


@db_connection.executor
def list_column(cursor, db_table):
    query = util.query_builder('SELECT', db_table, '*')
    cursor.execute(query)

    return [dict(row) for row in cursor.fetchall()]


@db_connection.executor
def get_headers(cursor, db_table):
    return list(list_column(db_table)[0].keys())


def question_display(question_id, db_table):
    db_data, headers = list_column(db_table), get_headers(db_table)
    answers = [answer for answer in list_column('answer')
               if int(answer['question_id']) == question_id]

    for question in db_data:
        if int(question['id']) == question_id:
            return question, headers, answers


@db_connection.executor
def answer_display(answer_id):
    # todo: unprepared for sql
    list_of_answers = csv_connection.csv_opening(ANSWERS)
    for answer in list_of_answers:
        if int(answer['id']) == int(answer_id):
            return answer


@db_connection.executor
def add_question(cursor, requested_data, requested_image, db_table):
    path = files_connection.upload_file(requested_image)
    if path:
        values = [str(v) for v in [util.current_date(), '0', '0', requested_data['title'], requested_data['message'], path]]
    else:
        values = [str(v) if v else v for v in [util.current_date(), '0', '0', requested_data['title'],
                                               requested_data['message'], None]]

    query = util.query_builder('INSERT', db_table)
    cursor.execute(query, values)

    return dict(cursor.fetchone())['id']


@db_connection.executor
def answer_question(cursor, requested_data, requested_image, db_table, question_id):
    path = files_connection.upload_file(requested_image)
    if path:
        values = [str(v) for v in
                  [util.current_date(), 0, question_id, requested_data['message'], path]]
    else:
        values = [str(v) if v else v for v in [util.current_date(), 0, question_id, requested_data['message'], None]]

    query = util.query_builder('INSERT', db_table)
    cursor.execute(query, values)


@db_connection.executor
def voting_for_up_down(cursor, db_table, given_id, up_or_down):
    values = {'up': "+ 1", 'down': "- 1"}

    query = util.query_builder('VOTING', db_table, update=values[up_or_down], condition=f'id = {given_id}',
                               col_to_update='vote_number')
    cursor.execute(query)

    if db_table == 'answer':
        return dict(cursor.fetchone())['question_id']


@db_connection.executor
def record_edit(cursor, db_table, given_id, columns, values):
    # csv_connection.csv_editing(file, given_id, keys=keys, values_to_update=values)
    # todo: unprepared for sql

    query = util.query_builder('EDITING', db_table, given_id, cols_to_update=columns, condition=f'id = {given_id}')
    cursor.execute(query, values)


@db_connection.executor
def record_delete(cursor, db_table, given_id):
    query = util.query_builder('DELETE', db_table, condition=f'id = {given_id}')
    cursor.execute(query)

    if db_table == 'answer':
        return dict(cursor.fetchone())['question_id']


@db_connection.executor
def five_latest_questions(cursor, question):
    # todo: unprepared for query_builder

    query = """
    SELECT *
    FROM question    
    ORDER BY id DESC
    LIMIT 5;
    """
    cursor.execute(query, [question])

    return cursor.fetchall()


@db_connection.executor
def get_tag_names_by_question_id(cursor, question_id):
    # todo: unprepared for query_builder

    query = """
        SELECT name
        FROM tag
        RIGHT JOIN question_tag
        ON tag.id = question_tag.tag_id
        WHERE question_id = %s
    """
    cursor.execute(query, [question_id])

    return cursor.fetchall()


@db_connection.executor
def get_tags(cursor):
    # todo: unprepared for query_builder

    query = """
        SELECT name
        FROM tag
        ORDER BY id ASC 
    """
    cursor.execute(query)

    return cursor.fetchall()


@db_connection.executor
def get_new_id(cursor):
    # todo: unprepared for query_builder
    # unnecessary because of auto setting of id value
    query = """
        SELECT MAX(id)
        AS max_id
        FROM tag
    """
    cursor.execute(query)

    return int(cursor.fetchone().get('max_id')) + 1


@db_connection.executor
def add_tag(cursor, new_tag):
    # todo: unprepared for query_builder

    query = """
        INSERT INTO tag
        VALUES (%s, %s)
    """
    # unnecessary line because of auto setting of id value:
    tag_id = get_new_id()
    cursor.execute(query, [tag_id, new_tag])


@db_connection.executor
def get_tags_id(cursor, tags):
    # todo: unprepared for query_builder
    get_id = []
    for tag in tags:
        query = """
            SELECT id
            FROM tag
            WHERE name LIKE %s
        """
        cursor.execute(query, [tag])
        get_id.append(cursor.fetchall())
    return get_id


@db_connection.executor
def insert_updated_tags(cursor, question_id, new_tags):
    # todo: unprepared for query_builder
    tags_already_in = [tag['name'] for tag in get_tag_names_by_question_id(question_id)]
    tags_to_add = [tag for tag in new_tags if tag not in tags_already_in]
    for id_list in get_tags_id(tags_to_add):
        for selected_id in id_list:
            query = """
                INSERT INTO question_tag (question_id, tag_id)
                VALUES (%s, %s)
            """
            cursor.execute(query, [question_id, selected_id['id']])


@db_connection.executor
def get_new_id(cursor):
    # todo: unprepared for query_builder
    # unnecessary because of auto setting of id value

    query = """
        SELECT MAX(id)
        AS max_id
        FROM comment
    """
    cursor.execute(query)
    return int(cursor.fetchone().get('max_id')) + 1


@db_connection.executor
def add_comment_to_question(cursor, requested_data, question_id):
    # todo: unprepared for query_builder

    new_values = (get_new_id(), util.current_date(), question_id, requested_data['message'], 0)
    query = """
        INSERT INTO comment (id, submission_time, question_id, message, edited_count)
        VALUES (%s, %s, %s, %s, %s);
        """
    return cursor.execute(query, new_values)


@db_connection.executor
def add_comment_to_answer(cursor, requested_data, question_id, answer_id):
    # todo: unprepared for query_builder

    new_values = (get_new_id(), util.current_date(), question_id, answer_id, requested_data['message'], 0)
    query = """
        INSERT INTO comment (id, submission_time, question_id, answer_id, message, edited_count)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
    return cursor.execute(query, new_values)


@db_connection.executor
def delete_comment(cursor, id):
    # todo: record delete to use for deleting a comment
    # todo: unprepared for query_builder

    query = """
        DELETE FROM comment
        WHERE id = %s
        RETURNING question_id;
        """

    cursor.execute(query, [id])
    return dict(cursor.fetchone())['question_id']
