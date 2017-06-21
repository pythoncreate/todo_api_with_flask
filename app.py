from flask import Flask, g, jsonify, render_template

from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr

from auth import auth
import config
import models
from resources.todo import todo_api

import config

app = Flask(__name__)
app.register_blueprint(todo_api, url_prefix='/api/v1')
app.register_blueprint(users_api, url_prefix='/api/v1')

limiter = Limiter(app, global_limits=[config.DEFAULT_RATE], key_func=get_ipaddr)
limiter.limit("40/day")(users_api)
limiter.limit(config.DEFAULT_RATE, per_method=True,
              methods=["post", "put", "delete"])(todo_api)

@app.route('/')
def my_todos():
    return render_template('index.html')

@app.route('/api/v1/users/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})

if __name__ == '__main__':
    models.initialize()
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)