import os
from flask import Flask, render_template, request, redirect, url_for

import connection
import data_manager


app = Flask(__name__)
# GLOBAL directory for the app config
UPLOAD_FOLDER_A = os.environ.get('UPLOAD_FOLDER_A')
UPLOAD_FOLDER_Q = os.environ.get('UPLOAD_FOLDER_Q')
# GLOBAL directories to our CSV files:
QUESTIONS = 'data/questions.csv'
ANSWERS = 'data/answers.csv'


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/list', methods=['get'])
def list_questions():
    global QUESTIONS, ANSWERS
    data, headers = data_manager.list_questions(QUESTIONS)

    return render_template('list.html', data=data, headers=headers)


@app.route('/question/<int:question_id>', methods=['get'])
def question_display(question_id):
    global QUESTIONS, ANSWERS
    question_to_display, headers, answers = data_manager.question_display(question_id, QUESTIONS, ANSWERS)

    return render_template('question.html', question=question_to_display, headers=headers, answers=answers)


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def question_edit(question_id):
    global QUESTIONS, ANSWERS
    if request.method == 'GET':
        question_to_edit = data_manager.question_display(question_id, QUESTIONS, ANSWERS)[0]

        return render_template('question_edit.html', question=question_to_edit)

    elif request.method == 'POST':
        edited_question = dict(request.form)
        keys, values = list(edited_question.keys()), list(edited_question.values())
        connection.csv_editing(QUESTIONS, question_id, keys=keys, values_to_update=values)

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


@app.route('/question/<question_id>/new_answer', methods=['GET', 'POST'])
def answer_question(question_id):
    qid = int(question_id)

    if request.method == 'GET':
        return render_template('answer_question.html', question_id=qid)

    elif request.method == 'POST':
        data = dict(request.form)
        data["id"] = data_manager.get_next_id()
        data["submission_time"] = 0
        data["vote_number"] = 0
        data["question_id"] = qid

        image = request.files['image']

        if image.filename != '':
            path = (f"{UPLOAD_FOLDER_A}/{image.filename}")
            image.save(path)
            data["image"] = "/" + path

        connection.csv_appending(ANSWERS, data)

        return redirect(url_for('question_display', question_id=qid))


@app.route('/add_question', methods=['GET'])
def display_add_question():
    return render_template('ask.html')


@app.route('/add_question', methods=['POST'])
def add_question():
    data = dict(request.form)
    data["id"] = data_manager.get_next_id()
    data["view_number"] = 0
    data["vote_number"] = 0

    image = request.files['image']
    if image.filename != '':
        path = (f"{UPLOAD_FOLDER_Q}/{image.filename}")
        image.save(path)
        data["image"] = "/" + path


    connection.csv_appending(QUESTIONS, data)
    return redirect(url_for("question_display", question_id=data["id"]))


if __name__ == "__main__":
    app.run()
