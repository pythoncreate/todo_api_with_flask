import unittest
import json

from playhouse.test_utils import test_database
from peewee import *

from app import app
from models import User, ToDo


USER_DATA = {
    'username': 'testuser',
    'email': 'testuser@test.com',
    'password': 'pass@#$@',
    'verify_password': 'pass@#$@'
}
TODO_LIST = ['Brush Teeth', 'Go Hiking', 'Complete Treehouse Course']


class TodoTestCase(unittest.TestCase):
    def create_test_todos(self):
        for todo in TODO_LIST:
            ToDo.create(name=todo, user=USER_DATA)

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app
        self.client = app.test_client()


class TodoResourceTestCase(TodoTestCase):
    def test_get_todos(self):
        with test_database(TEST_DB, (ToDo,)):
            ToDo.create(name="Test code using unittests")
            self.assertEqual(ToDo.select().count(), 1)

    def test_authorized_add_todo(self):
        with test_database(TEST_DB, (ToDo, User)):
            user = User.create_user(**USER_DATA)
            token = user.generate_auth_token().decode('ascii')
            headers = {'Authorization': 'Token {}'.format(token)}

            resp = self.client.post('/api/v1/todos', data={'name': 'bowling'}, headers=headers)
            resp_data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 201)
            self.assertTrue('bowling' == resp_data['name'])

    def test_unauthorized_add_todo(self):
        with test_database(TEST_DB, (ToDo,)):
            resp = self.client.post('/api/v1/todos', data={'name': 'Test 2'})
            self.assertEqual(resp.status_code, 200)


class UserModelTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app
        self.client = app.test_client()

    @staticmethod
    def create_users(count=2):
        for i in range(count):
            User.create_user(
                username='test_user_{}'.format(i),
                email='test_{}@example.com'.format(i),
                password='password'
            )

    def test_create_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            self.assertEqual(User.select().count(), 2)
            self.assertNotEqual(
                User.select().get().password,
                'password'
            )


if __name__ == '__main__':
    TEST_DB = SqliteDatabase(':memory:')
    TEST_DB.connect()
    TEST_DB.create_tables([User, ToDo], safe=True)
    unittest.main()
