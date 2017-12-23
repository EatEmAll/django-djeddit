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
        'meta',
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

SiteMap
-------

If you'd like djeddit to generate sitemaps for SEO you can follow these steps.
Djeddit comes with a sitemaps.py file included and you just have to enable it.

Add the following apps to your installed apps if they are not already there

.. code-block:: python

    'django.contrib.sites',
    'django.contrib.sitemaps',

Create the sitemaps dictionary with the djeddit sitemap and core django sitemap imports in the urls.py of your project

.. code-block:: python
    from django.contrib.sitemaps.views import sitemap
    from djeddit.sitemaps import ThreadSitemap

    sitemaps = {
        'djeddit' : ThreadSitemap
    }
Now add the following to your `urlpatterns`

.. code-block:: python

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

Run migrations and run server

If you visit `sitemap.xml` on your site you should have a working sitemap for djeddit threads.
