import csv
import os


def get_headers(csv_file):
    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        headers = next(reader)
    return headers


def csv_opening(csv_file):
    # simple function to operate on .csv file - generating dictionary for each line with keys corresponding with
    # column name. function returns a list of dictionaries.

    csv_into_dictionaries = []

    with open(csv_file, 'r') as file:
        for line in csv.DictReader(file):
            csv_into_dictionaries.append(line)

    return csv_into_dictionaries


def csv_creating(csv_file, dict_to_add=None):
    with open(csv_file, 'w') as file:
        csv_writer = csv.writer(file)
        if dict_to_add:
            csv_writer.writerow(dict_to_add)


def csv_appending(csv_file, dict_to_add):
    with open(csv_file, 'a') as file:
        dict_appender = csv.DictWriter(file, fieldnames=get_headers(csv_file))
        dict_appender.writerow(dict_to_add)

    return dict_to_add['id']


def csv_editing(csv_file, given_id, keys=None, values_to_update=None, method=None):
    with open(csv_file, 'r') as file:
        headers = get_headers(csv_file)
        data = csv.DictReader(file)
        temp_data = []
        question_id_return = None

        for row in data:
            if int(row['id']) == given_id:
                if method == 'add':
                    row['vote_number'] = str(int(row['vote_number']) + 1)
                    if 'question_id' in row.keys():
                        question_id_return = row['question_id']
                elif method == 'subtract':
                    row['vote_number'] = str(int(row['vote_number']) - 1)
                    if 'question_id' in row.keys():
                        question_id_return = row['question_id']
                else:
                    for key, value in zip(keys, values_to_update):
                        row[key] = value
                temp_data.append(row)
            else:
                temp_data.append(row)

    with open(csv_file, 'w') as file:
        dict_writer = csv.DictWriter(file, delimiter=',', fieldnames=headers)
        dict_writer.writeheader()
        dict_writer.writerows(temp_data)

    if question_id_return:
        return question_id_return


def csv_delete_row(csv_file, question_id):
    with open(csv_file, 'r') as file:
        headers = get_headers(csv_file)
        data = csv.DictReader(file)
        temp_data = []
        question_id_return = None
        for row in data:
            if int(row['id']) != question_id:
                temp_data.append(row)
            else:
                print(row['image'])
                if 'question_id' in row.keys():
                    question_id_return = row['question_id']
                if row['image'] != '':
                    os.remove(row['image'])

    with open(csv_file, 'w') as file:
        dict_writer = csv.DictWriter(file, delimiter=',', fieldnames=headers)
        dict_writer.writeheader()
        dict_writer.writerows(temp_data)

    if question_id_return:
        return question_id_return


def upload_file(given_image, folder):
    if given_image.filename != '':
        path = f"{folder}/{given_image.filename}"
        given_image.save(path)

        return path
