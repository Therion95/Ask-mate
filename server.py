from flask import Flask, render_template, url_for, request, redirect

import data_manager, connection


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/list', methods=['get'])
def list_questions():
    data, headers = data_manager.list_questions('data/questions.csv')
    return render_template('list.html', data=data, headers=headers)


@app.route('/question/<int:question_id>')
def question_display(question_id):
    pass


@app.route('/add_question', methods=['GET'])
def display_add_question():
    return render_template('Ask_a_question.html')


@app.route('/add_question', methods=['POST'])
def add_question():
    data = dict(request.form)
    data["id"] = data_manager.get_next_id()
    data["view_number"] = 0
    data["vote_number"] = 0
    connection.csv_appending('data/questions.csv', data)
    return redirect(url_for("question_display"))


if __name__ == "__main__":
    app.run()
