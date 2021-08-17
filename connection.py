import csv


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
    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        i = next(reader)
        print(i)

    with open(csv_file, 'a', newline='') as file:
        dict_appender = csv.DictWriter(file, fieldnames=i)
        dict_appender.writerow(dict_to_add)

