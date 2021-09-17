import bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash, session
import db_data_manager
import util

app = Flask(__name__)
app.config['SECRET_KEY'] = "sa37f2$fs(#fskj34"
TEMPLATES_AUTO_RELOAD = True


# --------------------------------------------------------


# INDEX page
@app.route("/")
def index():
    latest_questions = db_data_manager.get_five_latest_questions()
    return render_template('index.html', headers=latest_questions[0].keys(), questions=latest_questions)


# --------------------------------------------------------
# REGISTRATION AND LOGIN
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        user_data = dict(request.form)
        if db_data_manager.save_data_if_correct(user_data):
            return redirect(url_for('index'))
    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        user = db_data_manager.get_hash(email)
        if util.verify_password(request.form['password'], user['hash']):
            session['user'] = {'id': user['id'], 'email': email, 'user_name': user['user_name']}
            flash('You are logged in!')
            return redirect(url_for('index'))
        else:
            flash('Incorrect data')
            return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out!')
    return redirect(url_for('index'))


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
# LST OF ALL USERS WITH ALL DETAILS
@app.route('/users', methods=['GET'])
def list_of_users():
    get_users_data = db_data_manager.get_details_of_users()
    get_headers_from_users_db = get_users_data[0].keys()
    return render_template('users_list.html', data=get_users_data, headers=get_headers_from_users_db,
                           list_of_headers=list(get_headers_from_users_db))


# SELECTED USER PAGE

@app.route('/user/<int:user_id>', methods=['GET'])
def display_selected_user(user_id):
    if not util.is_logged_in():
        return redirect(url_for('index'))
    if user_id != util.get_user_id_from_session():
        flash("It's not you!")
        return redirect(url_for('list_of_users'))
    get_user_data = db_data_manager.get_details_of_specific_user(user_id)
    get_headers_from_user_db = get_user_data[0].keys()
    get_question_data = db_data_manager.get_data_from_table_by_user_id('question', user_id)
    get_answer_data = db_data_manager.get_data_from_table_by_user_id('answer', user_id)
    get_comment_data = db_data_manager.get_data_from_table_by_user_id('comment', user_id)
    return render_template('user.html', data=get_user_data, headers=get_headers_from_user_db,
                           questions=get_question_data, answers=get_answer_data, comments=get_comment_data)

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



# DISPLAY
@app.route('/question/<int:question_id>', methods=['GET'])
def question_display(question_id):
    tags = db_data_manager.get_tag_names_by_question_id(question_id)
    question_to_display, headers, answers, comments, comments_a = db_data_manager.get_question_data_display(
        question_id, 'question')
    return render_template('question.html', question=question_to_display, headers=headers, answers=answers,
                               comments=comments, comments_a=comments_a, tags=tags)


@app.route('/tags')
def display_tag_page():
    tags = db_data_manager.get_tags_names_and_numbers()
    return render_template('tags.html', tags=tags)


@app.route('/list-by-tag/<tag_name>')
def display_list_questions_by_tag(tag_name):
    data = db_data_manager.get_questions_by_tag(tag_name)
    headers = data[0].keys()
    return render_template('questions_by_tag.html', data=data, headers=headers)

# --------------------------------------------------------


# ADDING QUESTIONS, ANSWERS, COMMENTS, TAGS pages
@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'GET':
        if request.cookies.get('session'):
            return render_template('ask.html')
        else:
            flash('Only for logged in users')
            return redirect(url_for('index'))

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
        db_data_manager.add_comment(requested_data, answer_id=answer_id, question_id=question_id)

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
    question_id = db_data_manager.get_record_to_edit(answer_id, 'answer')['question_id']

    return redirect(url_for('question_display', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote_down', methods=['GET'])
def answer_voting_down(answer_id):
    db_data_manager.voting_for_up_down('answer', answer_id, 'down')
    question_id = db_data_manager.get_record_to_edit(answer_id, 'answer')['question_id']

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
        answer_to_edit = db_data_manager.get_record_to_edit(answer_id, 'answer')

        return render_template('answer_edit.html', answer=answer_to_edit)

    elif request.method == 'POST':
        edited_answer = dict(request.form)
        new_image = request.files['image']
        db_data_manager.record_edit('answer', answer_id,
                                    list(edited_answer.keys()), list(edited_answer.values()),
                                    given_file=new_image)
        question_id = db_data_manager.get_record_to_edit(answer_id, 'answer')['question_id']

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if request.method == 'GET':
        comment_to_edit = db_data_manager.get_record_to_edit(comment_id, 'comment')

        return render_template('comment_edit.html', comment=comment_to_edit)

    elif request.method == 'POST':
        edited_comment = dict(request.form)
        edited_comment['submission_time'] = util.current_date()
        db_data_manager.get_the_number_of_edits(comment_id)
        question_id = db_data_manager.record_edit('comment', comment_id, list(edited_comment.keys()), list(edited_comment.values()))

        return redirect(url_for('question_display', question_id=question_id['question_id']))


@app.route('/question/<int:question_id>/new-tag', methods=['GET', 'POST'])
def assign_tag_to_question(question_id):
    if request.method == 'GET':
        tags = db_data_manager.get_tags_to_choose(question_id)

        return render_template('new_tag.html', question_id=question_id, tags=tags)

    elif request.method == 'POST':
        tags = request.form.getlist('tag')
        db_data_manager.insert_updated_tags(question_id, tags)

        return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/<int:answer_id>/<option>', methods=['GET'])
def mark_an_answer(question_id, answer_id, option):
    db_data_manager.mark_an_answer(answer_id, option)
    return redirect(url_for("question_display", question_id=question_id))

# --------------------------------------------------------


# DELETE SOMETHING pages
@app.route('/question/<int:question_id>/delete', methods=['GET'])
def question_delete(question_id):
    db_data_manager.record_delete('question', 'id', question_id)

    return redirect(url_for('list_questions'))


@app.route('/answer/<int:answer_id>/delete', methods=['GET'])
def answer_delete(answer_id):
    question_id = db_data_manager.get_record_to_edit(answer_id, 'answer')['question_id']
    db_data_manager.record_delete('comment', 'answer_id', answer_id)
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


@app.route('/comments/question<int:question_id>/comment<int:comment_id>/delete', methods=['GET'])
def delete_question_comment(question_id, comment_id):
    db_data_manager.record_delete('comment', 'id', comment_id)
    return redirect(url_for('question_display', question_id=question_id))


@app.route('/comments/question<int:question_id>/comment<int:comment_id>/delete_comment_answer', methods=['GET'])
def delete_answer_comment(comment_id, question_id):
    db_data_manager.record_delete('comment', 'id', comment_id)
    return redirect(url_for('question_display', question_id=question_id))


@app.route('/question/<int:question_id>/tag/<int:tag_id>/delete', methods=['GET'])
def delete_tag(question_id, tag_id):
    db_data_manager.delete_tag(question_id, tag_id)

    return redirect(url_for('question_display', question_id=question_id))

# --------------------------------------------------------


if __name__ == "__main__":
    app.run()
