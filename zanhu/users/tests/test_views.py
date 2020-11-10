from django.test import RequestFactory
from test_plus.test import TestCase
from zanhu.users.views import UserUpdateView, UserRedirectView
from zanhu.users.models import User  # !

class BaseUserTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = self.make_user()
        self.User = User()  # !


class TestUserUpdateView(BaseUserTestCase):

    def setUp(self):
        super().setUp()
        self.view = UserUpdateView()
        request = self.factory.get('/fake-url')
        request.user = self.user
        self.view.request = request

    def test_get_success_url(self):
        self.assertEqual(self.view.get_success_url(), '/users/testuser/')

    def test_get_object(self):
        self.assertEqual(self.view.get_object(), self.User.objects.get(username=self.view.request.user.username))


class TestUserRedirectView(BaseUserTestCase):

    def setUp(self):
        super().setUp()
        self.view = UserRedirectView()

    def test_get_redirect_url(self):
        self.assertEqual(self.view.get_redirect_url(), '/users/testuser/')
