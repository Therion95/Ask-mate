import os
from flask import Flask, render_template, request, redirect, url_for

import data_manager, connection

UPLOAD_FOLDER = 'static/answer_images'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# GLOBAL directories to our CSV files:
QUESTIONS = 'data/questions.csv'
ANSWERS = 'data/answers.csv'


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/list', methods=['get'])
def list_questions():
    global QUESTIONS
    data, headers = data_manager.list_questions(QUESTIONS)
    return render_template('list.html', data=data, headers=headers)


@app.route('/question/<int:question_id>', methods=['get'])
def question_display(question_id):
    global QUESTIONS
    question_to_display, headers, answers = data_manager.question_display(question_id, QUESTIONS, ANSWERS)
    return render_template('question.html', question=question_to_display, headers=headers, answers=answers)


# TODO: get_or_404()

@app.route('/answer', methods=['GET'])
def display_answer_question():
    return render_template('answer_question.html')


@app.route('/answer', methods=['POST'])
def answer_question():
    if 'image' not in request.files:
        return "There is no file in form"
    image = request.files['image']
    path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(path)

    data = dict(request.form)
    data["id"] = data_manager.get_next_id(ANSWERS)
    data["submission_time"] = 0
    data["vote_number"] = 0
    data["question_id"] = 0
    data['image'] = path
    print(data)
    connection.csv_appending(ANSWERS, data)

    return redirect(url_for('index'))


@app.route('/add_question', methods=['GET'])
def display_add_question():
    return render_template('Ask_a_question.html')


@app.route('/add_question', methods=['POST'])
def add_question():
    data = dict(request.form)
    data["id"] = data_manager.get_next_id(QUESTIONS)
    data["view_number"] = 0
    data["vote_number"] = 0
    connection.csv_appending('data/questions.csv', data)
    return redirect(url_for("question_display"))


if __name__ == "__main__":
    app.run()
