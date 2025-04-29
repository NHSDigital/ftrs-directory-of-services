import csv


def get_csv_data(file_name):
    with open(file_name, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        rows = list(csv_reader)
    return rows


def csv_row_count(file_name):
    row_count = len(get_csv_data(file_name))
    return row_count


def csv_column_count(file_name):
    column_count = len(get_csv_data(file_name)[0])
    return column_count


def csv_headers(file_name):
    csv_headers = get_csv_data(file_name)[0]
    return csv_headers


def assert_cell_value(file_name, rownum, colnum):
    rownum = int(rownum)
    colnum = int(colnum)
    cell_value = get_csv_data(file_name)[rownum][colnum]
    return cell_value
