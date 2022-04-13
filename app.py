import logging
import os

import flask
from flask import request, jsonify, render_template, flash, url_for
from werkzeug.exceptions import InternalServerError
from werkzeug.utils import redirect, secure_filename

from database.connection import Database
from utils.helpers import get_from_env, dict_factory

DATABASE = get_from_env("DATABASE")
HOST = get_from_env("DB_HOST")
PORT = get_from_env("DB_PORT")
USER = get_from_env("DB_USER")
PASS = get_from_env("DB_PASS")
CONNECTION = Database(DATABASE, USER, PASS, HOST, PORT)
UPLOAD_FOLDER = 'static'

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = 'eW96YXVr'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(filename='record.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


@app.route('/', methods=['GET'])
def home():
    rows = CONNECTION.execute_select_statement("*", "doors_")
    return render_template("index.html", rows=rows)


@app.route('/door', methods=['GET'])
def doors():
    rows = CONNECTION.execute_select_statement("*", "doors_")
    return render_template("door.html", rows=rows)


@app.route('/new-door', methods=['GET', 'POST'])
def add_new_door():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        size = request.form['size']
        color = request.form['color']
        image = request.files['image']

        if image.filename != '':
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
            query = f"0, \"{name}\", {price}, \"{size}\", \"{color}\", \"{image.filename}\""

            CONNECTION.row_factory = dict_factory
            CONNECTION.execute_insert_statement("doors_", query)
            return redirect(url_for('.index'))

    return render_template("create.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/api/v1/resources/doors/all', methods=['GET'])
def api_all():
    CONNECTION.row_factory = dict_factory
    all_doors = CONNECTION.execute_select_statement("*", "doors_")

    return jsonify(all_doors)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.errorhandler(InternalServerError)
def handle_500(e):
    original = getattr(e, "original_exception", None)
    return "<h1>500</h1><p>The resource could not be found.</p>", 500


@app.route('/api/v1/resources/doors/add', methods=['POST'])
def add_door():
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        data = request.get_json()
    else:
        return 'Content-Type not supported!'

    query = f"{data['id']}, \"{data['name']}\", {data['price']}, \"{data['size']}\", \"{data['color']}\""

    CONNECTION.row_factory = dict_factory
    results = CONNECTION.execute_insert_statement("doors_", query)

    return jsonify(results)


@app.route('/api/v1/resources/doors/<int:door_id>', methods=['PATCH'])
def update_door(door_id):
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        data = request.get_json()
    else:
        return 'Content-Type not supported!'

    CONNECTION.row_factory = dict_factory

    update_query = ""
    for key in data.keys():
        update_query += f"{key} = \"{data[key]}\", "
    update_query = update_query[:-2]
    results = CONNECTION.execute_update_statement("doors_", update_query, "id", door_id)

    return jsonify(results)


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
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
