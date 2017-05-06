=============================
django-djeddit
=============================

.. image:: https://badge.fury.io/py/django-djeddit.svg
    :target: https://badge.fury.io/py/django-djeddit

.. image:: https://travis-ci.org/EatEmAll/django-djeddit.svg?branch=master
    :target: https://travis-ci.org/EatEmAll/django-djeddit

.. image:: https://codecov.io/gh/EatEmAll/django-djeddit/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/EatEmAll/django-djeddit

Bare bones Django forum application with Reddit like features

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

And djeddit_settings to context_processors:

.. code-block:: python
    
    'context_processors': [
        ...
        'djeddit.context_processors.djeddit_settings',
        ...
    ]

Add django-djeddit's URL patterns:

.. code-block:: python

    urlpatterns = [
        ...
        url(r'^', include('djeddit.urls')),
        ...
    ]
    
Migrate models:

.. code-block::

    python manage.py migrate djeddit

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
