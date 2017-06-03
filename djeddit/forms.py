from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from django import forms

from .models import Topic, Thread, Post


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'description']

    def __init__(self, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('submit', 'Submit', css_class='btn btn-primary'))


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'url']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
