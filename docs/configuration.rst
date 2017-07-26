=============
Configuration
=============

To use django-djeddit in a project, add it to your `INSTALLED_APPS`:

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

.. code-block:: python

    python manage.py migrate djeddit

Additional Options
------------------

By default the base template is djeddit/base.html

You can change the default base template in settings.py:

.. code-block:: python

    DJEDDIT_BASE_TEMPLATE = "path/to/template.html"

In order for the base template to work properly with the app's templtes it needs to contain the following:

within <head>...</head>:

.. code-block:: python

    {% load staticfiles %}
    {% include 'djeddit/base_stylesheets.html' %}

within <body>...</body>:

.. code-block:: python

    {% block title %}{% endblock %}
    {% block content %}{% endblock %}
    {% block scripts %}{% endblock %}
    {% include 'djeddit/base_scripts.html' %}
    {% block scripts %}{% endblock %}

You can use the structue of djeddit/base.html for reference.
