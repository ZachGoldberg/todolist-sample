import random
import string

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
            }

    def get_token(self, user):
        response = self.client.post(self.AUTH_URL, user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        return token

    def test_add_todoitem(self):
        data = self.sample_todoitem()
        user = self.create_user()
        token = self.get_token(user)
        response = self.client.post(self.TODO_URL, data)
        print response
        import pdb; pdb.set_trace()


    def test_edit_todoitem(self):
        pass

    def test_delete_todoitem(self):
        pass

    def test_remove_users_and_todo(self):
        pass

    def test_list_todoitem(self):
        pass
