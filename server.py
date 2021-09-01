import os
from flask import Flask, render_template, request, redirect, url_for

import csv_connection
import db_data_manager
import util

app = Flask(__name__)
# GLOBAL directory for the app config
UPLOAD_FOLDER_A = os.environ.get('UPLOAD_FOLDER_A')
UPLOAD_FOLDER_Q = os.environ.get('UPLOAD_FOLDER_Q')
# GLOBAL directories to our CSV files:
QUESTIONS = os.environ.get('QUESTIONS_PATH')
ANSWERS = os.environ.get('ANSWERS_PATH')


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/list', methods=['GET'])
def list_questions():
    # CSV version:

    # global QUESTIONS, ANSWERS
    # data, headers = data_manager.list_questions(QUESTIONS)
    #
    # return render_template('list.html', data=data, headers=headers)

    # DB version:
    db_data = db_data_manager.list_column('question')
    db_headers = db_data[0].keys()
    return render_template('list.html', data=db_data, headers=db_headers)


@app.route('/question/<int:question_id>', methods=['GET'])
def question_display(question_id):
    # CSV version:

    # global QUESTIONS, ANSWERS
    # question_to_display, headers, answers = data_manager.question_display(question_id, QUESTIONS, ANSWERS)
    #
    # return render_template('question.html', question=question_to_display, headers=headers, answers=answers)

    # DB version:

    question_to_display, headers, answers = db_data_manager.question_display(question_id, 'question')

    return render_template('question.html', question=question_to_display, headers=headers, answers=answers)


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def question_edit(question_id):
    global QUESTIONS, ANSWERS
    if request.method == 'GET':
        question_to_edit = db_data_manager.question_display(question_id, 'question')[0]

        return render_template('question_edit.html', question=question_to_edit)

    elif request.method == 'POST':
        edited_question = dict(request.form)
        db_data_manager.record_edit('question', question_id, tuple(edited_question.keys()), list(edited_question.values()))

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/answer/<int:answer_id>/edit', methods=['GET', 'POST'])
def answer_edit(answer_id):
    if request.method == 'GET':
        answer_to_edit = db_data_manager.display_answer(answer_id)

        return render_template('answer_edit.html', answer=answer_to_edit)

    elif request.method == 'POST':
        edited_answer = dict(request.form)
        question_id = int(db_data_manager.display_answer(answer_id)['question_id'])
        db_data_manager.record_edit('answer', answer_id, list(edited_answer.keys()), list(edited_answer.values()))

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/delete', methods=['GET'])
def question_delete(question_id):
    # global QUESTIONS
    # db_data_manager.record_delete('answer', )
    db_data_manager.record_delete('question', question_id)


    return redirect(url_for('list_questions'))


@app.route('/answer/<int:answer_id>/delete', methods=['GET'])
def answer_delete(answer_id):
    # global ANSWERS
    question_id = db_data_manager.record_delete('answer', answer_id)

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/vote_up', methods=['GET'])
def question_voting_up(question_id):
    # global QUESTIONS
    # data_manager.voting_for_up_down(QUESTIONS, question_id, 'add')

    db_data_manager.voting_for_up_down('question', question_id, 'up')
    return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/vote_down', methods=['GET'])
def question_voting_down(question_id):
    global QUESTIONS
    # data_manager.voting_for_up_down(QUESTIONS, question_id, 'subtract')

    db_data_manager.voting_for_up_down('question', question_id, 'down')
    return redirect(url_for('question_display', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote_up', methods=['GET'])
def answer_voting_up(answer_id):
    global ANSWERS
    question_id = db_data_manager.voting_for_up_down('answer', answer_id, 'up')

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote_down', methods=['GET'])
def answer_voting_down(answer_id):
    global ANSWERS
    question_id = db_data_manager.voting_for_up_down('answer', answer_id, 'down')

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'GET':

        return render_template('ask.html')

    elif request.method == 'POST':
        requested_data = dict(request.form)
        requested_image = request.files['image']
        new_id = db_data_manager.add_question(requested_data, requested_image, 'question')

        return redirect(url_for("question_display", question_id=new_id))


@app.route('/question/<int:question_id>/new_answer', methods=['GET', 'POST'])
def answer_question(question_id):
    if request.method == 'GET':
        return render_template('answer_question.html', question_id=question_id)

    elif request.method == 'POST':
        requested_data = dict(request.form)
        requested_image = request.files['image']
        db_data_manager.answer_question(requested_data, requested_image, 'answer', question_id)

        return redirect(url_for('question_display', question_id=question_id))


if __name__ == "__main__":
    app.run()
