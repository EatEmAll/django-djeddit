=============================
django-djeddit
=============================

.. image:: https://badge.fury.io/py/django-djeddit.svg
    :target: https://badge.fury.io/py/django-djeddit

.. image:: https://travis-ci.org/EatEmAll/django-djeddit.svg?branch=master
    :target: https://travis-ci.org/EatEmAll/django-djeddit

.. image:: https://codecov.io/gh/EatEmAll/django-djeddit/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/EatEmAll/django-djeddit

Bare bones Django forum application with Reddit like features. 

* `django-mptt library <https://github.com/django-mptt/django-mptt>`_ is used to display threads in a collapsable tree structure
* compatible with mobile screen sizes (using `Bootstrap <https://github.com/twbs/bootstrap>`_)
* voting functionality for threads & comments

`django-registration-redux <https://github.com/macropin/django-registration>`_ is recommanded to go along with this app if you need out of the box user registration functionality.

Documentation
-------------

The full documentation is at https://django-djeddit.readthedocs.io.

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

You can use New Topic dialog in /topics page if you're logged in as a superuser or you can create one in a python console:

.. code-block:: python

    from djeddit.models import Topic
    Topic.objects.create(title='Test Topic')

Launch the app and go to /topics page.

Features
--------

* TODO

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
