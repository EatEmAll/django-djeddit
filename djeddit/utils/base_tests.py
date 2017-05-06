from django.contrib.auth.models import User


def createUser(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    user.save()
    return user

class TestCalls(object):

    def __init__(self, template=''):
        self.template = template
        self.user = None

    def login(self):
        if self.username and self.password:
            self.client.login(username=self.username, password=self.password)

    @classmethod
    def _setup_user(cls, username, email, password):
        cls.user = createUser(username, email, password)
        cls.username = username
        cls.password = password

    def _test_call_view_loads(self, url, data=None):
        data = data or {}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.template)

    def _test_call_view_submit(self, url, data=None, redirect=False):
        data = data or {}
        response = self.client.post(url, data)
        expected_code = 302 if redirect else 200
        self.assertEqual(response.status_code, expected_code)
        if self.template:
            self.assertTemplateUsed(self.template)

    def _test_call_view_require_login(self, url, data=None):
        data = data or {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def _test_call_view_redirects(self, url, redirected_url, data=None):
        data = data or {}
        response = self.client.get(url, data)
        self.assertRedirects(response, redirected_url)

    def _test_call_view_code(self, url, code, data=None):
        data = data or {}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, code)
