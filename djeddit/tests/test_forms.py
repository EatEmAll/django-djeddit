from django.test import TestCase
from djeddit.forms import TopicForm, ThreadForm

# Create your tests here.


class TopicFormTest(TestCase):
    def testIsValid(self):
        tf = TopicForm(dict(title='Test Topic'))
        self.assertTrue(tf.is_valid())

    def testEmpty(self):
        tf = TopicForm()
        self.assertTrue(not tf.is_valid())


class ThreadFormTest(TestCase):
    def testIsValid(self):
        tf = ThreadForm(dict(title='Test Thread'))
        self.assertTrue(tf.is_valid())

    def testEmpty(self):
        tf = TopicForm()
        self.assertTrue(not tf.is_valid())
