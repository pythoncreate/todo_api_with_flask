from flask import Blueprint, abort

from flask_restful import (Resource, Api, reqparse,
                           inputs, fields, marshal,
                           marshal_with, url_for)

from auth import auth
import models

todo_fields = {
    'id': fields.Integer,
    'name': fields.String
}


def todo_or_404(todo_id):
    try:
        todo = models.ToDo.get(models.ToDo.id==todo_id)
    except models.ToDo.DoesNotExist:
        abort(404)
    else:
        return todo


class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No todo name provided',
            location=['form','json']
        )
        super().__init__()

    def get(self):
        todos = [marshal(todo, todo_fields)
                 for todo in models.ToDo.select()]
        return {'todos':todos}

    @marshal_with(todo_fields)
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        todo = models.ToDo.create(**args)
        return (todo, 201,
                {'Location': url_for('resources.todos.todo', id=todo.id)}
                )


class Todo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No todo name provided',
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(todo_fields)
    def get(self, id):
        return todo_or_404(id)

    @marshal_with(todo_fields)
    @auth.login_required
    def put(self, id):
        args = self.reqparse.parse_args()
        query = models.ToDo.update(**args).where(models.ToDo.id==id)
        query.execute()
        return (models.ToDo.get(models.ToDo,id==id), 200,
                {'Location': url_for('resources.todos.todo', id=id)})

    @auth.login_required
    def delete(self, id):
        query = models.ToDo.delete().where(models.ToDo.id == id)
        query.execute()
        return ('', 204,
                {'Location': url_for('resources.todos.todos')})

todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(
    TodoList,
    '/api/v1/todos',
    endpoint='todos'
)
api.add_resource(
    Todo,
    '/api/v1/todos/<int:id>',
    endpoint='todo'
)