from flask import Flask, render_template, request, redirect, url_for


import data_manager

app = Flask(__name__)

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
    data = dict(request.form)
    print(data)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
