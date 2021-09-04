import os
from flask import Flask, render_template, request, redirect, url_for

import db_data_manager
import files_connection

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
    questions = db_data_manager.list_column('question')
    latest_questions = db_data_manager.five_latest_questions(questions)
    headers = questions[0].keys()
    return render_template('index.html', headers=headers, questions=latest_questions)


@app.route('/list', methods=['GET'])
def list_questions():
    db_data = db_data_manager.list_column('question')
    db_headers = db_data[0].keys()
    return render_template('list.html', data=db_data, headers=db_headers)


@app.route('/question/<int:question_id>', methods=['GET'])
def question_display(question_id):
    tags = db_data_manager.get_tag_names_by_question_id(question_id)
    question_to_display, headers, answers, comments, comments_a = db_data_manager.question_display(question_id, 'question')

    return render_template('question.html', question=question_to_display, headers=headers, answers=answers,
                           comments=comments, comments_a=comments_a, tags=tags)


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def question_edit(question_id):
    # global QUESTIONS, ANSWERS, COMMENTS_Q, COMMENTS_A
    if request.method == 'GET':
        question_to_edit = db_data_manager.question_display(question_id, 'question')[0]
        # question_to_edit = db_data_manager.question_display(question_id, 'question')[0]

        return render_template('question_edit.html', question=question_to_edit)

    elif request.method == 'POST':
        edited_question = dict(request.form)
        # csv_connection.csv_editing(QUESTIONS, question_id, keys=list(edited_question.keys()),
        #                        values_to_update=list(edited_question.values()))
        new_image = request.files['image']
        db_data_manager.record_edit('question', question_id, list(edited_question.keys()), list(edited_question.values()), given_file=new_image, given_folder=UPLOAD_FOLDER_Q)

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/answer/<int:answer_id>/edit', methods=['GET', 'POST'])
def answer_edit(answer_id):
    if request.method == 'GET':
        answer_to_edit = db_data_manager.record_to_edit(answer_id)

        return render_template('answer_edit.html', answer=answer_to_edit)
# ASIA:
#     elif request.method == 'POST':
#         edited_answer = dict(request.form)
#         new_image = request.files['image']
#         data_manager.edit_answer(answer_id, edited_answer, new_image)
#         question_id = int(data_manager.display_answer(answer_id)['question_id'])
#
#         return redirect(url_for('question_display', question_id=question_id))

    elif request.method == 'POST':
        edited_answer = dict(request.form)
        new_image = request.files['image']
        # question_id = int(db_data_manager.display_answer(answer_id)['question_id'])
        question_id = db_data_manager.record_edit('answer', answer_id, list(edited_answer.keys()), list(edited_answer.values()), given_file=new_image, given_folder=UPLOAD_FOLDER_A)

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


@app.route('/answer/<int:answer_id>/delete-image', methods=['GET'])
def delete_image(answer_id):
    db_data_manager.delete_image(answer_id, 'answer')
    return redirect(url_for('answer_edit', answer_id=answer_id))


@app.route('/question/<int:question_id>/delete-image', methods=['GET'])
def delete_image_q(question_id):
    db_data_manager.delete_image(question_id, 'question')

    return redirect(url_for('question_edit', question_id=question_id))


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
        db_data_manager.answer_question(requested_data, requested_image, question_id)

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/new_comment', methods=['GET', 'POST'])
def add_comment_to_question(question_id):
    if request.method == 'GET':
        return render_template('comment_question.html', question_id=question_id)
    elif request.method == 'POST':
        requested_data = dict(request.form)
        db_data_manager.add_comment_to_question(requested_data, question_id)

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/<int:answer_id>/new_comment', methods=['GET', 'POST'])
def add_comment_to_answer(question_id, answer_id):
    if request.method == 'GET':
        return render_template('comment_answer.html', answer_id=answer_id)
    elif request.method == 'POST':
        requested_data = dict(request.form)
        db_data_manager.add_comment_to_answer(requested_data, answer_id)

        return redirect(url_for('question_display', answer_id=answer_id))


@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if request.method == 'GET':
        comment_to_edit = db_data_manager.record_to_edit(comment_id)

        return render_template('comment_edit.html', comment=comment_to_edit)
    # ASIA:
    #     elif request.method == 'POST':
    #         edited_answer = dict(request.form)
    #         new_image = request.files['image']
    #         data_manager.edit_answer(answer_id, edited_answer, new_image)
    #         question_id = int(data_manager.display_answer(answer_id)['question_id'])
    #
    #         return redirect(url_for('question_display', question_id=question_id))

    elif request.method == 'POST':
        edited_comment = dict(request.form)
        question_id = db_data_manager.record_edit('comment', comment_id, list(edited_comment.keys()),
                                                  list(edited_comment.values()))

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/comments/<int:given_id>/delete', methods=['GET'])
def delete_comment(given_id):
    # question_id = db_data_manager.delete_comment(id)
    question_id = db_data_manager.record_delete('comment', given_id)
    return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/new-tag', methods=['GET', 'POST'])
def new_tag(question_id):
    if request.method == 'GET':
        tags = db_data_manager.get_tags_to_choose(question_id)

        return render_template('new_tag.html', question_id=question_id, tags=tags)

    elif request.method == 'POST':
        tags = request.form.getlist('tag')
        db_data_manager.insert_updated_tags(question_id, tags)

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/define-new-tag', methods=['POST'])
def define_new_tag(question_id):
    tag = dict(request.form)
    db_data_manager.add_tag(tag['new_tag'])

    return redirect(url_for('new_tag', question_id=question_id))


@app.route('/question/<int:question_id>/tag/<int:tag_id>/delete', methods=['GET'])
def delete_tag(question_id, tag_id):
    db_data_manager.delete_tag(question_id, tag_id)

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/search', methods=['GET', 'POST'])
def search_results():
    if request.method == 'POST':
        word = dict(request.form)['search']
        data = db_data_manager.searching(word)
        headers = data[0].keys()

        return render_template('search_results.html', data=data, headers=headers)


if __name__ == "__main__":
    app.run()
