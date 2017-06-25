from flask import Flask, render_template, g, jsonify

import models
from resources.todos import todos_api
from resources.users import users_api
from auth import auth


import config

app = Flask(__name__)
app.register_blueprint(todos_api)
app.register_blueprint(users_api, url_prefix='/api/v1')


@app.route('/')
def my_todos():
    todos = models.ToDo.select().limit(50)
    return render_template('index.html', todos=todos)


@app.route('/api/v1/users/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    token=g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})

if __name__ == '__main__':
    models.initialize()
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)