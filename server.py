from flask import Flask, render_template

import data_manager

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


if __name__ == "__main__":
    app.run()
