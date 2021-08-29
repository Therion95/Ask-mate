import os
from flask import Flask, render_template, request, redirect, url_for

import connection
import data_manager
import util

app = Flask(__name__)
# GLOBAL directory for the app config
UPLOAD_FOLDER_A = os.environ.get('UPLOAD_FOLDER_A')
UPLOAD_FOLDER_Q = os.environ.get('UPLOAD_FOLDER_Q')
# GLOBAL directories to our CSV files:
QUESTIONS = os.environ.get('QUESTIONS_PATH')
ANSWERS = os.environ.get('ANSWERS_PATH')
COMMENTS_Q = os.environ.get('COMMENTS_Q')
COMMENTS_A = os.environ.get('COMMENTS_A')


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/list', methods=['GET'])
def list_questions():
    global QUESTIONS, ANSWERS
    data, headers = data_manager.list_questions(QUESTIONS)

    return render_template('list.html', data=data, headers=headers)


@app.route('/question/<int:question_id>', methods=['GET'])
def question_display(question_id):
    global QUESTIONS, ANSWERS, COMMENTS_Q, COMMENTS_A
    question_to_display, headers, answers, comments, comments_a = data_manager.question_display(question_id, QUESTIONS,
                                                                                        ANSWERS, COMMENTS_Q, COMMENTS_A)

    return render_template('question.html', question=question_to_display, headers=headers, answers=answers,
                           comments=comments, comments_a=comments_a)


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def question_edit(question_id):
    global QUESTIONS, ANSWERS, COMMENTS_Q, COMMENTS_A
    if request.method == 'GET':
        question_to_edit = data_manager.question_display(question_id, QUESTIONS, ANSWERS, COMMENTS_Q, COMMENTS_A)[0]

        return render_template('question_edit.html', question=question_to_edit)

    elif request.method == 'POST':
        edited_question = dict(request.form)
        connection.csv_editing(QUESTIONS, question_id, keys=list(edited_question.keys()),
                               values_to_update=list(edited_question.values()))

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/answer/<int:answer_id>/edit', methods=['GET', 'POST'])
def answer_edit(answer_id):
    if request.method == 'GET':
        answer_to_edit = data_manager.display_answer(answer_id)

        return render_template('answer_edit.html', answer=answer_to_edit)

    elif request.method == 'POST':
        edited_answer = dict(request.form)
        question_id = int(data_manager.display_answer(answer_id)['question_id'])
        connection.csv_editing(ANSWERS, answer_id, keys=list(edited_answer.keys()),
                               values_to_update=list(edited_answer.values()))

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/delete', methods=['GET'])
def question_delete(question_id):
    global QUESTIONS
    connection.csv_delete_row(QUESTIONS, question_id)

    return redirect(url_for('list_questions'))


@app.route('/answer/<int:answer_id>/delete', methods=['GET'])
def answer_delete(answer_id):
    global ANSWERS
    question_id = connection.csv_delete_row(ANSWERS, answer_id)

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/vote_up', methods=['GET'])
def question_voting_up(question_id):
    global QUESTIONS
    connection.csv_editing(QUESTIONS, question_id, method='add')

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/vote_down', methods=['GET'])
def question_voting_down(question_id):
    global QUESTIONS
    connection.csv_editing(QUESTIONS, question_id, method='subtract')

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote_up', methods=['GET'])
def answer_voting_up(answer_id):
    global ANSWERS
    question_id = connection.csv_editing(ANSWERS, answer_id, method='add')

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote_down', methods=['GET'])
def answer_voting_down(answer_id):
    global ANSWERS
    question_id = connection.csv_editing(ANSWERS, answer_id, method='subtract')

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'GET':

        return render_template('ask.html')

    elif request.method == 'POST':
        requested_data = dict(request.form)
        requested_image = request.files['image']
        new_id = data_manager.add_question(requested_data, requested_image)

        return redirect(url_for("question_display", question_id=new_id))


@app.route('/question/<int:question_id>/new_answer', methods=['GET', 'POST'])
def answer_question(question_id):
    if request.method == 'GET':
        return render_template('answer_question.html', question_id=question_id)

    elif request.method == 'POST':
        requested_data = dict(request.form)
        requested_image = request.files['image']
        data_manager.answer_question(requested_data, requested_image, question_id)

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/new_comment', methods=['GET', 'POST'])
def add_comment_to_question(question_id):
    if request.method == 'GET':
        return render_template('comment_question.html',  question_id=question_id)
    elif request.method == 'POST':
        requested_data = dict(request.form)
        data_manager.comment_question(requested_data, question_id)

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/<int:answer_id>/new_comment', methods=['GET', 'POST'])
def add_comment_to_answer(question_id, answer_id):
    if request.method == 'GET':
        return render_template('comment_answer.html',  answer_id=answer_id, question_id=question_id)
    elif request.method == 'POST':
        requested_data = dict(request.form)
        data_manager.comment_answer(requested_data, answer_id, question_id)

        return redirect(url_for('question_display', answer_id=answer_id, question_id=question_id))


if __name__ == "__main__":
    app.run()
