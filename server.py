from flask import Flask, render_template, request, redirect, url_for, flash, session
import db_data_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = "sa37f2$fs(#fskj34"


# --------------------------------------------------------


# INDEX page
@app.route("/")
def index():
    latest_questions = db_data_manager.get_five_latest_questions()
    return render_template('index.html', headers=latest_questions[0].keys(), questions=latest_questions)


# --------------------------------------------------------
# REGISTRATION
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        user_data = dict(request.form)
        if db_data_manager.save_data_if_correct(user_data):
            return redirect(url_for('index'))
    return render_template('registration.html')


# ---------------------------------------------------------


# SEARCH ENGINE on index page
@app.route('/search', methods=['GET', 'POST'])
def search_results():
    if request.method == 'POST':
        word = dict(request.form)['search']
        data = db_data_manager.get_searched_phrases(word)
        if data:
            headers = data[0].keys()
            return render_template('search_results.html', data=data, headers=headers)

        else:
            flash('No results')
            return redirect(url_for('index'))


# --------------------------------------------------------


# LIST QUESTIONS page
@app.route('/list', methods=['GET', 'POST'])
def list_questions():
    if request.method == 'GET':
        db_data = db_data_manager.get_listed_column('question')
        db_headers = db_data[0].keys()

        return render_template('list.html', data=db_data, headers=db_headers, list_of_headers=list(db_headers))
    elif request.method == 'POST':
        order_by, order_direction = dict(request.form)['header'], dict(request.form)['sort']
        db_data = db_data_manager.get_sorted_questions(order_by, order_direction)
        db_headers = db_data[0].keys()

        return render_template('list.html', data=db_data, headers=db_headers, list_of_headers=list(db_headers))


# --------------------------------------------------------


# QUESTION DISPLAY page
@app.route('/question/<int:question_id>', methods=['GET'])
def question_display(question_id):
    tags = db_data_manager.get_tag_names_by_question_id(question_id)
    question_to_display, headers, answers, comments, comments_a = db_data_manager.get_question_data_display(question_id,
                                                                                                            'question')

    return render_template('question.html', question=question_to_display, headers=headers, answers=answers,
                           comments=comments, comments_a=comments_a, tags=tags)


# --------------------------------------------------------


# ADDING QUESTIONS, ANSWERS, COMMENTS, TAGS pages
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
def add_answer_question(question_id):
    if request.method == 'GET':

        return render_template('answer_question.html', question_id=question_id)

    elif request.method == 'POST':
        requested_data = dict(request.form)
        requested_image = request.files['image']
        db_data_manager.answer_question(requested_data, requested_image, 'answer', question_id)

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/new_comment', methods=['GET', 'POST'])
def add_comment_question(question_id):
    if request.method == 'GET':

        return render_template('comment_question.html', question_id=question_id)

    elif request.method == 'POST':
        requested_data = dict(request.form)
        db_data_manager.add_comment(requested_data, question_id=question_id)

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/<int:answer_id>/new_comment', methods=['GET', 'POST'])
def add_comment_answer(question_id, answer_id):
    if request.method == 'GET':

        return render_template('comment_answer.html', question_id=question_id, answer_id=answer_id)

    elif request.method == 'POST':
        requested_data = dict(request.form)
        db_data_manager.add_comment(requested_data, answer_id=answer_id)

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/define-new-tag', methods=['POST'])
def define_new_tag(question_id):
    tag = dict(request.form)
    db_data_manager.add_tag(tag['new_tag'])

    return redirect(url_for('assign_tag_to_question', question_id=question_id))


# --------------------------------------------------------


# VOTING ON QUESTIONS & ANSWERS endpoints
@app.route('/question/<int:question_id>/vote_up', methods=['GET'])
def question_voting_up(question_id):
    db_data_manager.voting_for_up_down('question', question_id, 'up')

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/vote_down', methods=['GET'])
def question_voting_down(question_id):
    db_data_manager.voting_for_up_down('question', question_id, 'down')

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote_up', methods=['GET'])
def answer_voting_up(answer_id):
    db_data_manager.voting_for_up_down('answer', answer_id, 'up')
    question_id = db_data_manager.get_record_to_edit(answer_id)['question_id']

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote_down', methods=['GET'])
def answer_voting_down(answer_id):
    db_data_manager.voting_for_up_down('answer', answer_id, 'down')
    question_id = db_data_manager.get_record_to_edit(answer_id)['question_id']

    return redirect(url_for('question_display', question_id=question_id))


# --------------------------------------------------------


# EDIT something
@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def question_edit(question_id):
    if request.method == 'GET':
        question_to_edit = db_data_manager.get_question_data_display(question_id, 'question')[0]

        return render_template('question_edit.html', question=question_to_edit)

    elif request.method == 'POST':
        edited_question = dict(request.form)
        new_image = request.files['image']
        db_data_manager.record_edit('question', question_id, list(edited_question.keys()),
                                    list(edited_question.values()), given_file=new_image)

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/answer/<int:answer_id>/edit', methods=['GET', 'POST'])
def answer_edit(answer_id):
    if request.method == 'GET':
        answer_to_edit = db_data_manager.get_record_to_edit(answer_id)

        return render_template('answer_edit.html', answer=answer_to_edit)

    elif request.method == 'POST':
        edited_answer = dict(request.form)
        new_image = request.files['image']
        db_data_manager.record_edit('answer', answer_id,
                                    list(edited_answer.keys()), list(edited_answer.values()),
                                    given_file=new_image)
        question_id = db_data_manager.get_record_to_edit(answer_id)['question_id']

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if request.method == 'GET':
        comment_to_edit = db_data_manager.get_record_to_edit(comment_id)

        return render_template('comment_edit.html', comment=comment_to_edit)

    elif request.method == 'POST':
        edited_comment = dict(request.form)
        question_id = db_data_manager.record_edit('comment', comment_id, list(edited_comment.keys()),
                                                  list(edited_comment.values()))

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/new-tag', methods=['GET', 'POST'])
def assign_tag_to_question(question_id):
    if request.method == 'GET':
        tags = db_data_manager.get_tags_to_choose(question_id)

        return render_template('new_tag.html', question_id=question_id, tags=tags)

    elif request.method == 'POST':
        tags = request.form.getlist('tag')
        db_data_manager.insert_updated_tags(question_id, tags)

        return redirect(url_for('question_display', question_id=question_id))


# --------------------------------------------------------


# DELETE SOMETHING pages
@app.route('/question/<int:question_id>/delete', methods=['GET'])
def question_delete(question_id):
    db_data_manager.record_delete('question', 'id', question_id)

    return redirect(url_for('list_questions'))


@app.route('/answer/<int:answer_id>/delete', methods=['GET'])
def answer_delete(answer_id):
    question_id = db_data_manager.get_record_to_edit(answer_id)['question_id']
    db_data_manager.record_delete('answer', 'id', answer_id)

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/answer/<int:answer_id>/delete-image', methods=['GET'])
def delete_answer_image(answer_id):
    db_data_manager.delete_image(answer_id, 'answer')
    return redirect(url_for('answer_edit', answer_id=answer_id))


@app.route('/question/<int:question_id>/delete-image', methods=['GET'])
def delete_question_image(question_id):
    db_data_manager.delete_image(question_id, 'question')

    return redirect(url_for('question_edit', question_id=question_id))


@app.route('/comments//<int:question_id>/delete', methods=['GET'])
def delete_question_comment(question_id):
    db_data_manager.record_delete('comment', 'question_id', question_id)

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/comments/<int:answer_id>/delete', methods=['GET'])
def delete_answer_comment(answer_id):
    db_data_manager.record_delete('comment', 'answer_id', answer_id)
    question_id = db_data_manager.get_record_to_edit(answer_id)['question_id']

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/tag/<int:tag_id>/delete', methods=['GET'])
def delete_tag(question_id, tag_id):
    db_data_manager.delete_tag(question_id, tag_id)

    return redirect(url_for('question_display', question_id=question_id))


# --------------------------------------------------------


if __name__ == "__main__":
    app.run()
