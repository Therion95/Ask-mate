import connection



def list_questions(csv_file):
    list_of_data = connection.csv_opening(csv_file)

    headers = list(list_of_data[0].keys())

    return list_of_data, headers

def get_headers(csv_file):
    list_of_data = connection.csv_opening(csv_file)

    return list(list_of_data[0].keys())



def question_display():
    pass

def get_next_id():
    data, headers = list_questions('data/questions.csv')
    return int(max([head["id"] for head in data])) + 1






