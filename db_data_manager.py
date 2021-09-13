import os

import bcrypt as bcrypt
from flask import flash, session, request

import db_connection
import files_connection
import util

# GLOBAL directory for the app config
UPLOAD_FOLDER_A = os.environ.get('UPLOAD_FOLDER_A')
UPLOAD_FOLDER_Q = os.environ.get('UPLOAD_FOLDER_Q')


@db_connection.executor
def get_listed_column(cursor, db_table):
    query = f'''
    SELECT *
    FROM {db_table}
    ORDER BY {db_table}.id
    '''

    cursor.execute(query)

    return [dict(row) for row in cursor.fetchall()]


@db_connection.executor
def get_listed_column_names(cursor, db_table):
    query = f'''
    SELECT *
    FROM {db_table}
    LIMIT 0
    '''

    cursor.execute(query)

    return [desc[0] for desc in cursor.description][1:]


@db_connection.executor
def get_question_data_display(cursor, question_id, db_table):
    db_data, headers = get_listed_column(db_table), get_listed_column_names(db_table)

    for question in db_data:
        if int(question['id']) == question_id:
            answers = [answer for answer in get_listed_column('answer')
                       if int(answer['question_id']) == question_id]
            user = [user for user in get_listed_column('users')
                    if int(user['id']) == question['user_id']]
            question_comments, comments_to_answers = None, {}

            query = f'''
            SELECT *
            FROM comment
            WHERE question_id = {question_id}
            '''

            cursor.execute(query)
            q_temp = cursor.fetchall()

            if q_temp:
                question_comments = [dict(row) for row in q_temp]
            if answers:
                answer_ids = [k['id'] for k in answers]

                for answer_id in answer_ids:
                    query = f'''
                    SELECT *
                    FROM comment
                    WHERE answer_id = {answer_id}
                    '''

                    cursor.execute(query)
                    a_temp = cursor.fetchall()
                    if a_temp:
                        comments_to_answers[answer_id] = [dict(row) for row in a_temp]

            return question, headers, answers, question_comments, comments_to_answers, user


@db_connection.executor
def get_list_of_questions(cursor):
    query = f'''
    SELECT q.id, u.user_name ,q.submission_time, q.view_number, q.vote_number, q.title, q.message, q.image
    FROM question as q
    LEFT JOIN users as u
    ON q.user_id = u.id
    ORDER BY q.id
    '''

    cursor.execute(query)

    return [dict(row) for row in cursor.fetchall()]


@db_connection.executor
def get_record_to_edit(cursor, given_id):
    query = f'''
    SELECT *
    FROM answer
    WHERE id = {given_id}
    '''

    cursor.execute(query)

    return dict(cursor.fetchone())


@db_connection.executor
def get_searched_phrases(cursor, word):
    query = f"""
        SELECT question.*
        FROM question
        LEFT JOIN answer
        ON question.id = answer.question_id
        WHERE title LIKE '{word}'
        OR question.message LIKE '{word}'
        OR answer.message LIKE '{word}'
    """
    cursor.execute(query)
    return cursor.fetchall()


@db_connection.executor
def get_sorted_questions(cursor, header, sort):
    query = f'''
        SELECT *
        FROM question
        ORDER BY {header} {sort}
    '''

    cursor.execute(query)

    return cursor.fetchall()


@db_connection.executor
def get_tags(cursor):
    query = '''
        SELECT name, id
        FROM tag
        ORDER BY id
    '''

    cursor.execute(query)

    return cursor.fetchall()


def get_tags_to_choose(question_id):
    all_tags = [tag['name'] for tag in get_tags()]
    tags_for_id = [tag['name'] for tag in get_tag_names_by_question_id(question_id)]

    return [tag for tag in all_tags if tag not in tags_for_id]


@db_connection.executor
def get_tags_id(cursor, tags):
    get_id = []
    for tag in tags:
        query = f'''
            SELECT id
            FROM tag
            WHERE name LIKE '{tag}'
        '''

        cursor.execute(query)
        get_id.append(cursor.fetchall())

    return get_id

@db_connection.executor
def get_details_of_users(cursor):
    query = '''        
        SELECT users.id, user_name, registration_date, COUNT(DISTINCT question.id) AS asked_questions, 
        COUNT(DISTINCT answer.id) as answers, COUNT(DISTINCT comment.id) as comments, reputation
        FROM users
        LEFT JOIN question
        ON question.user_id = users.id
        LEFT JOIN answer
        ON question.user_id = answer.user_id
        LEFT JOIN comment
        ON question.user_id = comment.user_id        
        GROUP BY users.id, user_name, registration_date
        ORDER BY id
    '''

    cursor.execute(query)
    return cursor.fetchall()


@db_connection.executor
def get_details_of_specific_user(cursor, user_id):
    query = f'''
       SELECT users.id, user_name, registration_date, COUNT(DISTINCT question.id) AS asked_questions, 
        COUNT(DISTINCT answer.id) as answers, COUNT(DISTINCT comment.id) as comments, reputation
        FROM users
        LEFT JOIN question
        ON question.user_id = users.id
        LEFT JOIN answer
        ON question.user_id = answer.user_id
        LEFT JOIN comment
        ON question.user_id = comment.user_id       
        WHERE question.user_id = {user_id}
        GROUP BY users.id, user_name, registration_date
        ORDER BY id       
    '''
    cursor.execute(query)
    return cursor.fetchall()

@db_connection.executor
def get_data_from_table_by_user_id(cursor, db_table, user_id):
    if db_table == 'question':
        query = f'''
            SELECT id AS question_id, message, submission_time
            FROM {db_table}
            WHERE user_id = {user_id}
            ORDER BY question_id
            '''

    else:
        query = f'''
            SELECT question_id, message, submission_time
            FROM {db_table}
            WHERE user_id = {user_id}
            ORDER BY question_id
            '''

    cursor.execute(query)
    return cursor.fetchall()

@db_connection.executor
def get_logged_user_id(cursor):
    if request.cookies.get('session'):
        user_email = session.get('email')
        query = f"""
            SELECT id
            FROM users
            WHERE email = '{user_email}'
        """
        cursor.execute(query)
        return cursor.fetchone()['id']
    else:
        return None


# |-----------------------------------------|
# |ADDING QUESTIONS, ANSWERS, COMMENTS, TAGS|
# |_________________________________________|


@db_connection.executor
def add_question(cursor, requested_data, requested_image, db_table):
    path = files_connection.upload_file(requested_image, UPLOAD_FOLDER_Q)
    if path:
        values = [str(v) for v in [util.current_date(), '0', '0', requested_data['title'], requested_data['message'],
                                   path, get_logged_user_id()]]
    else:
        values = [str(v) if v else v for v in [util.current_date(), '0', '0', requested_data['title'],
                                               requested_data['message'], None, get_logged_user_id()]]

    columns = get_listed_column_names(db_table)
    query = f'''
    INSERT INTO {db_table} ({', '.join(columns)})
    VALUES ({', '.join(len(columns) * ['%s'])}) 
    RETURNING {db_table}.id;
    '''

    cursor.execute(query, values)

    return dict(cursor.fetchone())['id']


@db_connection.executor
def answer_question(cursor, requested_data, requested_image, db_table, question_id):
    path = files_connection.upload_file(requested_image, UPLOAD_FOLDER_A)
    if path:
        values = [str(v) for v in
                  [util.current_date(), 0, question_id, requested_data['message'], path, get_logged_user_id()]]
    else:
        values = [str(v) if v else v for v in [util.current_date(), 0, question_id, requested_data['message'], None,
                                               get_logged_user_id()]]

    columns = get_listed_column_names(db_table)
    query = f"""
    INSERT INTO {db_table} ({', '.join(columns)})
    VALUES ({', '.join(len(columns) * ['%s'])}) 
    RETURNING {db_table}.id;
    """

    cursor.execute(query, values)


@db_connection.executor
def add_comment(cursor, requested_data, question_id=None, answer_id=None):
    if answer_id and question_id:
        values = [str(v) if v else v for v in [question_id, answer_id, requested_data['message'], util.current_date(), 0,
                                               get_logged_user_id()]]
    elif question_id and answer_id is None:
        values = [str(v) if v else v for v in [question_id, None, requested_data['message'], util.current_date(), 0,
                                               get_logged_user_id()]]

    columns = get_listed_column_names('comment')
    query = f'''
    INSERT INTO comment ({', '.join(columns)})
    VALUES ({', '.join(len(columns) * ['%s'])}) 
    '''

    return cursor.execute(query, values)


@db_connection.executor
def add_tag(cursor, new_tag):
    columns = get_listed_column_names('tag')
    query = f'''
        INSERT INTO tag ({', '.join(columns)})
        VALUES ('{new_tag}')
        '''

    cursor.execute(query)


# |------------------------------------|
# |EDITING QUESTIONS, ANSWERS, COMMENTS|
# |____________________________________|


@db_connection.executor
def record_edit(cursor, db_table, given_id, columns, values, given_file=None):
    if given_file:
        if db_table == 'question':
            path = files_connection.upload_file(given_file, UPLOAD_FOLDER_Q)
        if db_table == 'answer':
            path = files_connection.upload_file(given_file, UPLOAD_FOLDER_A)

        columns.append('image')
        values.append(path)

    if len(columns) > 1:
        query = f'''
        UPDATE {db_table} 
        SET ({', '.join(columns)}) = ({', '.join(len(columns) * ['%s'])}) 
        WHERE {db_table}.id = {given_id}
        '''

        cursor.execute(query, values)

    else:
        query = f'''
        UPDATE {db_table} 
        SET {''.join(columns)} = '{''.join(values)}'
        WHERE {db_table}.id = {given_id}
        '''

        cursor.execute(query)


@db_connection.executor
def voting_for_up_down(cursor, db_table, given_id, up_or_down):
    values = {'up': "+ 1", 'down': "- 1"}

    query = f'''
    UPDATE {db_table}
    SET vote_number = vote_number {values[up_or_down]}
    WHERE id = {given_id}
    '''

    cursor.execute(query)


@db_connection.executor
def insert_updated_tags(cursor, question_id, new_tags):
    tags_already_in = [tag['name'] for tag in get_tag_names_by_question_id(question_id)]
    tags_to_add = [tag for tag in new_tags if tag not in tags_already_in]

    for id_list in get_tags_id(tags_to_add):
        for selected_id in id_list:
            query = """
                INSERT INTO question_tag (question_id, tag_id)
                VALUES (%s, %s)
            """

            cursor.execute(query, [question_id, selected_id['id']])


# |----------------|
# |    DELETING    |
# |________________|


@db_connection.executor
def record_delete(cursor, db_table, id_type, given_id):
    query = f'''
    DELETE FROM {db_table}
    WHERE {id_type} = {given_id}
    '''

    cursor.execute(query)


@db_connection.executor
def delete_tag(cursor, question_id, tag_id):
    query = f'''
        DELETE FROM question_tag
        WHERE question_id = {question_id}
        AND tag_id = {tag_id}
        '''

    cursor.execute(query)


@db_connection.executor
def delete_image(cursor, given_id, db_table):
    cursor.execute(f'''
    SELECT image 
    FROM {db_table} 
    WHERE id = {given_id}''')

    files_connection.delete_image(dict(cursor.fetchone())['image'])

    cursor.execute(f'''
    UPDATE {db_table} 
    SET image = NULL 
    WHERE id = {given_id} 
    RETURNING image''')


@db_connection.executor
def get_five_latest_questions(cursor):
    query = f'''
    SELECT *
    FROM question
    ORDER BY id DESC
    LIMIT 5
    '''

    cursor.execute(query)

    return cursor.fetchall()


@db_connection.executor
def get_tag_names_by_question_id(cursor, question_id):
    query = f'''
        SELECT name, id
        FROM tag
        RIGHT JOIN question_tag
        ON tag.id = question_tag.tag_id
        WHERE question_id = {question_id}
    '''

    cursor.execute(query)

    return cursor.fetchall()


@db_connection.executor
def add_new_user_to_db(cursor, user_data):
    password = user_data['password']
    hashed = (bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())).decode('utf-8')

    query = """
        INSERT INTO users (email, user_name, hash, registration_date, asked_questions, answers, comments, reputation)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, [user_data['email'], user_data['user_name'], hashed, util.current_date(), 0, 0, 0 ,0])


@db_connection.executor
def is_data_unique(cursor, column, user_data):
    query = f"""
        select id
        from users
        where {column} like '{user_data}'
    """
    cursor.execute(query)
    return False if cursor.fetchone() else True


def save_data_if_correct(user_data):
    if is_data_unique('email', user_data['email']):
        if is_data_unique('user_name', user_data['user_name']):
            if user_data['password'] == user_data['repeat_password']:
                add_new_user_to_db(user_data)
                flash("You have been register!")
                return True
            else:
                flash("Given passwords don't match")
        else:
            flash('User name is not available')
    else:
        flash('E-mail address is not available')


@db_connection.executor
def get_hash(cursor, email):
    query = """
    SELECT id, user_name, hash
    FROM users
    WHERE email = %s
    """
    cursor.execute(query, [email])
    return cursor.fetchone()


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf8'), hashed.encode('utf-8'))
