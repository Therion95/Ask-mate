import connection


def list_questions(csv_file):
    list_of_data = connection.csv_opening(csv_file)

    headers = list(list_of_data[0].keys())

    # TODO: implement order_by().all() functionality

    return list_of_data, headers


def question_display(question_id, csv_file):
    questions, headers = list_questions(csv_file)
    for question in questions:
        if int(question['id']) == question_id:
            return question, headers
