=============================
django-djeddit
=============================

.. image:: https://badge.fury.io/py/django-djeddit.svg
    :target: https://badge.fury.io/py/django-djeddit

.. image:: https://travis-ci.org/EatEmAll/django-djeddit.svg?branch=master
    :target: https://travis-ci.org/EatEmAll/django-djeddit

.. image:: https://codecov.io/gh/EatEmAll/django-djeddit/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/EatEmAll/django-djeddit

.. image:: https://img.shields.io/badge/python-2.7%2C%203.3%2C%203.4%2C%203.5-blue.svg
   :target: https://travis-ci.org/EatEmAll/django-djeddit

Bare bones Django forum application with Reddit like features developed as a Django reusable app.

* comments are ranked using wilson scoring interval and displayed in a collapsable tree structure (using `django-mptt <https://github.com/django-mptt/django-mptt>`_)
* voting functionality for threads & comments
* compatible with mobile screen sizes (using `Bootstrap <https://github.com/twbs/bootstrap>`_)
* users management page for admins
* admins can lock/unlock, edit, delete threads and posts, edit & delete topics


`django-registration-redux <https://github.com/macropin/django-registration>`_ is recommanded to go along with this app if you need out of the box user registration functionality.

Working demo: http://eatemall.pythonanywhere.com

Documentation: https://django-djeddit.readthedocs.io.

Screenshots
-----------

.. image:: https://raw.githubusercontent.com/EatEmAll/django-djeddit/master/media/Threads.jpg

.. image:: https://raw.githubusercontent.com/EatEmAll/django-djeddit/master/media/User.jpg

.. image:: https://raw.githubusercontent.com/EatEmAll/django-djeddit/master/media/Comments.jpg

Quickstart
----------

Install django-djeddit::

    pip install django-djeddit

Add it and its dependencies to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'crispy_forms',
        'mptt',
        'djeddit',
        ...
        ]

djeddit_settings to context_processors:

.. code-block:: python

    'context_processors': [
        ...
        'djeddit.context_processors.djeddit_settings',
        ...
    ]

jango-djeddit's URL patterns:

.. code-block:: python

    urlpatterns = [
        ...
        url(r'^', include('djeddit.urls')),
        ...
    ]

Migrate models:

.. code-block:: python

    python manage.py migrate djeddit


Create a topic:

You can use New Topic dialog in topics page if you're logged in as a superuser or you can create one in a python console:

.. code-block:: python

    from djeddit.models import Topic
    Topic.objects.create(title='Test Topic')


Credits
-------

Dependencies:

*  django-mptt_
*  crispy_forms_

.. _django-mptt: https://github.com/django-mptt/django-mptt
.. _crispy_forms: https://github.com/django-crispy-forms/django-crispy-forms

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
