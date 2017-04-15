=====
Usage
=====

To use django-djeddit in a project, add it to your `INSTALLED_APPS`:

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
