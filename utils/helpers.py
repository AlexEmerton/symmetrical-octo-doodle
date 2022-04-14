import os


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_from_env(var):
    """
    получаем данные из environment
    :param var:
    :return:
    """
    return os.environ.get(var)
