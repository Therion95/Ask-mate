from flask import Flask, render_template

import data_manager

app = Flask(__name__)


FILE_NAME = "C:\\Kurs_Programowania\\modul_web_codecool\\week1\\ask-mate-1-python-matysiewsky\\data\\questions.csv"


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/list', methods=['get'])
def list_questions():
    data, headers = data_manager.list_questions(FILE_NAME)
    return render_template('list.html', data=data, headers=headers)


@app.route('/question/<int:question_id>')
def question_display(question_id):
    pass


if __name__ == "__main__":
    app.run()
