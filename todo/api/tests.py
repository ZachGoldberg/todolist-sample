import random
import string

from api.models import TodoItem, TodoAttachment
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory


class AccountTests(APITestCase):
    USER_URL = "/api/users/"
    AUTH_URL = "/api/auth/"
    TODO_URL = "/api/todoitem/"

    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        username = "testuser"
        password = "secret"
        data = {'username': username, "password": password}
        response = self.client.post(self.USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))

        # Now try logging in, make sure that works
        response = self.client.post(self.AUTH_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        self.assertTrue(len(token) > 0)

    def create_user(self, username="testuser", password="secret"):
        data = {'username': username, "password": password}
        response = self.client.post(self.USER_URL, data)
        return data

    def test_list_users(self):
        self.create_user(username="user1")
        self.create_user(username="user2")

        response = self.client.get(self.USER_URL)
        users = set([u['username'] for u in response.data])
        self.assertTrue(users == set(["user1", "user2"]))

    def sample_todoitem(self):
        def randstr(N):
            return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
        return {
            "title": "title-%s" % randstr(5),
            "description": "description-%s" % randstr(20),
            "due_date": "2016-02-01T00:00",
            "status": True,
            "attachments": [{"data": "a1"}, {"data": "a2"}]
            }

    def set_token(self, user):
        response = self.client.post(self.AUTH_URL, user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        return token

    def test_add_todoitem(self):
        data = self.sample_todoitem()
        user = self.create_user()
        self.set_token(user)
        response = self.client.post(self.TODO_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TodoItem.objects.count(), 1)
        ti = TodoItem.objects.get()
        self.assertEqual(ti.title, data['title'])
        self.assertEqual(ti.description, data['description'])
        self.assertEqual(ti.status, data['status'])
        self.assertEqual(ti.attachments.count(), len(data["attachments"]))

    def test_edit_todoitem(self):
        # Create a new todo
        data = self.sample_todoitem()
        user = self.create_user()
        self.set_token(user)
        response = self.client.post(self.TODO_URL, data)

        # Change all it's fields
        ti_id = response.data['id']
        newdata = self.sample_todoitem()
        response = self.client.put("%s%s/" % (self.TODO_URL, ti_id),
                                   data=newdata)
        ti = TodoItem.objects.get(id=ti_id)
        self.assertEqual(ti.title, newdata['title'])
        self.assertEqual(ti.description, newdata['description'])
        self.assertEqual(ti.status, newdata['status'])

    def test_edit_attachment(self):
        data = self.sample_todoitem()
        user1 = self.create_user()
        self.set_token(user1)
        response = self.client.post(self.TODO_URL, data)
        ti_id = response.data['id']

        data["attachments"][0]["data"] = "new attachment data"
        response = self.client.put("%s%s/" % (self.TODO_URL, ti_id),
                                   data)
        tia_data = TodoItem.objects.get(id=ti_id).attachments.values_list("data", flat=True)
        self.assertTrue("new attachment data" in tia_data)


    def test_edit_attachment_wrong_user(self):
        data = self.sample_todoitem()
        user1 = self.create_user()
        self.set_token(user1)
        response = self.client.post(self.TODO_URL, data)
        ti_id = response.data['id']

        user2 = self.create_user("user2")
        self.set_token(user2)
        response = self.client.put("%s%s/" % (self.TODO_URL, ti_id),
                                   data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        tia_data = TodoItem.objects.get(id=ti_id).attachments.values_list("data", flat=True)
        self.assertFalse("new attachment data" in tia_data)


    def test_edit_wrong_todoitem(self):
        # Create a new todo for user 1
        data = self.sample_todoitem()
        user1 = self.create_user()
        self.set_token(user1)
        response = self.client.post(self.TODO_URL, data)

        # Create a user 2 and have them try and edit user 1's item
        user2 = self.create_user("user2")
        self.set_token(user2)
        newdata = self.sample_todoitem()
        response = self.client.put("%s%s/" % (self.TODO_URL,
                                              response.data['id']),
                                   data=newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        ti = TodoItem.objects.get()
        self.assertEqual(ti.title, data['title'])
        self.assertEqual(ti.description, data['description'])
        self.assertEqual(ti.status, data['status'])

    def test_delete_todoitem(self):
        data = self.sample_todoitem()
        user1 = self.create_user()
        self.set_token(user1)
        response = self.client.post(self.TODO_URL, data)
        ti = TodoItem.objects.get()
        response = self.client.delete("%s%s/" % (self.TODO_URL, ti.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TodoItem.objects.count(), 0)

    def test_list_todoitem(self):
        data1 = self.sample_todoitem()
        data2 = self.sample_todoitem()
        user1 = self.create_user()
        self.set_token(user1)
        response = self.client.post(self.TODO_URL, data1)
        response = self.client.post(self.TODO_URL, data2)

        self.assertEqual(TodoItem.objects.count(), 2)
        response = self.client.get(self.TODO_URL)
        todos = set([u['title'] for u in response.data])
        db_titles = set(TodoItem.objects.values_list('title', flat=True))
        self.assertTrue(db_titles == todos)

    def test_remove_users_and_todo(self):
        data1 = self.sample_todoitem()
        data2 = self.sample_todoitem()
        user1 = self.create_user()
        self.set_token(user1)
        response = self.client.post(self.TODO_URL, data1)
        response = self.client.post(self.TODO_URL, data2)
        response = self.client.delete("%s%s/" % (self.USER_URL, user1['username']))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TodoItem.objects.count(), 0)
        self.assertEqual(TodoAttachment.objects.count(), 0)
        self.assertEqual(User.objects.count(), 0)
