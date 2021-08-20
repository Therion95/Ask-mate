import connection



def list_questions(csv_file):
    list_of_data = connection.csv_opening(csv_file)

    headers = list(list_of_data[0].keys())

    # TODO: implement order_by().all() functionality

    return list_of_data, headers

def get_headers(csv_file):
    list_of_data = connection.csv_opening(csv_file)

    return list(list_of_data[0].keys())


def question_display(question_id, questions_csv_file, answers_csv_file):
    questions, headers = list_questions(questions_csv_file)
    answers = [answer for answer in connection.csv_opening(answers_csv_file)
               if int(answer['question_id']) == question_id]
    for question in questions:
        if int(question['id']) == question_id:
            return question, headers, answers


def get_next_id():
    data, headers = list_questions('data/questions.csv')
    # return int(max([head["id"] for head in data])) + 1
    return len(data) + 1





