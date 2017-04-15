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

Documentation
-------------

The full documentation is at https://django-djeddit.readthedocs.io.

Quickstart
----------

Install django-djeddit::

    pip install django-djeddit

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'djeddit.apps.DjedditConfig',
        ...
    )

Add django-djeddit's URL patterns:

.. code-block:: python

    from djeddit import urls as djeddit_urls


    urlpatterns = [
        ...
        url(r'^', include(djeddit_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
