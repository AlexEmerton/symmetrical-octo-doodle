import logging
import os

import flask
from flask import request, jsonify, render_template, flash, url_for, send_file
from werkzeug.exceptions import InternalServerError
from werkzeug.utils import redirect, secure_filename

from dao.door_dao import DoorDao
from database.database import Database
from models.door import Door
from utils.helpers import get_from_env, dict_factory

UPLOAD_FOLDER = 'static'

# получаем данные для соединения с БД
DATABASE = get_from_env("DATABASE")
HOST = get_from_env("DB_HOST")
PORT = get_from_env("DB_PORT")
USER = get_from_env("DB_USER")
PASS = get_from_env("DB_PASS")

# создаем соединение
CONNECTION = Database(DATABASE, USER, PASS, HOST, PORT)

# создаем приложение
app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = 'eW96YXVr'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# пишем логи в текстовый файл и в консоль
logging.basicConfig(filename='record.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# создаем обьект для управления БД для дверей
door_dao = DoorDao(CONNECTION)


@app.route('/', methods=['GET'])
def home():
    """
    сервис домашней страницы на /
    :return:
    """
    return render_template("index.html")


@app.route('/door', methods=['GET'])
def doors():
    """
    сервис страницы дверей. сначала получаем все двери, потом показываем
    :return:
    """
    all_doors = door_dao.get_all()
    return render_template("door.html", rows=all_doors)


@app.route('/download')
def download_file():
    """
    сервис для загрузки файла, прямая ссылка на статик файл
    :return:
    """
    path = "static/files/catalogue_doors.pdf"
    return send_file(path, as_attachment=True)


@app.route('/furniture', methods=['GET'])
def furniture():
    """
    сервис для страницы мебели
    :return:
    """
    # all_furniture = furniture_dao.get_all()
    return render_template("furniture.html")


@app.route('/fireplace', methods=['GET'])
def fireplace():
    """
    сервис для страницы каминов
    :return:
    """
    # all_furniture = furniture_dao.get_all()
    return render_template("camine.html")


@app.route('/admin', methods=['GET'])
def admin():
    return render_template("admin.html")


@app.route('/add-door', methods=['GET', 'POST'])
def add_new_door():
    """
    сервис для страницы добавления новой двери

    сначала извлекаем все текстовые данные из формы, превращаем их в обьект двери и отправляем в базу данных
    :return:
    """
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        size = request.form['size']
        color = request.form['color']
        image = request.files['image']

        if image.filename != '':
            # Сохраняем полученную картинку в папке с проектом
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if not name:
            flash('Name is required!')
        elif not price:
            flash('Price is required!')
        elif not size:
            flash('Size is required!')
        elif not color:
            flash('Color is required!')
        elif not image:
            flash('Image is required!')
        else:
            door = Door(0, name, price, size, color, image.filename)
            door_dao.add(door)
            return redirect(url_for('doors'))

    return render_template("create.html")


@app.route('/edit-door/<int:door_id>', methods=['GET', 'POST'])
def edit_door(door_id):
    """
    сервис для поправки двери.

    сначала получаем исходные данные двери по ID. дальше загружаем эти данные в форму, при отправлении формы
    обнавляем базу данных с новыми данными
    :param door_id:
    :return:
    """
    original_door = door_dao.get_by_id(door_id)

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        size = request.form['size']
        color = request.form['color']
        image = request.files['image']

        if image.filename != '':
            # Сохраняем полученную картинку в папке с проектом
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if not name:
            flash('Name is required!')
        elif not price:
            flash('Price is required!')
        elif not size:
            flash('Size is required!')
        elif not color:
            flash('Color is required!')
        elif not image:
            flash('Image is required!')
        else:
            new_door = Door(0, name, price, size, color, image.filename)
            door_dao.update(new_door, "Id", door_id)
            return redirect(url_for('edit_door', door_id=door_id))

    return render_template("edit_door.html", door=original_door)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.errorhandler(InternalServerError)
def handle_500(e):
    original = getattr(e, "original_exception", None)
    return "<h1>500</h1><p>The resource could not be found.</p>", 500


@app.route('/api/v1/resources/doors/all', methods=['GET'])
def api_all():
    all_doors = door_dao.get_all()
    return jsonify(all_doors)


@app.route('/api/v1/resources/doors/add', methods=['POST'])
def add_door():
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        data = request.get_json()
    else:
        return 'Content-Type not supported!'

    # MySQL сам обновляет ID рядов если мы устанавливаем его как 0
    # важно что так происходит потому что в БД мы сказали что ID как auto_increment то есть увеличивается сам
    door = Door(0, data['name'], data['price'], data['size'], data['color'], data['image'])
    return door_dao.add(door)


@app.route('/api/v1/resources/doors', methods=['GET'])
def api_filter():
    query_parameters = request.args
    logging.info(f"QUERY PARAMS: {query_parameters}")

    id = query_parameters.get('id')
    name = query_parameters.get('name')
    price = query_parameters.get('price')
    size = query_parameters.get('size')
    color = query_parameters.get('color')

    query = ""

    if id:
        query += f' id={id} AND'
    if name:
        query += f' name={name} AND'
    if price:
        query += f' price={price} AND'
    if size:
        query += f' size={size} AND'
    if color:
        query += f' color={color} AND'
    if not (id or name or price or size or color):
        return page_not_found(404)

    # remove trailing AND
    query = query[:-4] + ';'

    CONNECTION.row_factory = dict_factory
    results = CONNECTION.execute_select_where("*", "doors_", query)

    return jsonify(results)


if __name__ == '__main__':
    # запускаем приложение на порте 5000
    # важно что мы используем GUNICORN для запуска веб приложения в Heroku
    app.run(threaded=True, port=5000)
