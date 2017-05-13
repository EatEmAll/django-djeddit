=====
Configuration
=====

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

.. code-block::

    python manage.py migrate djeddit
    
=====
Additional Options
=====

By default the base template is djeddit/base.html

You can change it to something by adding this to settings.py:

.. code-block:: python

    DJEDDIT_BASE_TEMPLATE = "path/to/template.html"

