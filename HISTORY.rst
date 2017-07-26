.. :changelog:

History
-------

0.1.0 (2017-04-15)
++++++++++++++++++

* First release on PyPI.

0.1.5 (2017-05-26)
++++++++++++++++++

* Added tests for models, forms, views
* Urls that include topic titles with spaces in them don't work // fixed
* Competability fixes for Django 1.9 and 1.8 and Python 2.7
* client side fixes for added compatibility with mobile screen sizes
* font-awsome fonts are not loading // fixed
* Added description field for Topic model
* moved base.html to root template dir

0.2 (2017-07-04)
++++++++++++++++

* Admins can lock/unlock & delete threads, delete posts
* Admins can edit thread title, url, and post content
* added users management page for admins
* admins can edit & delete topics
* added fields upvotes, downvotes, wsi to Post model
* removed score field from Post model
* comments are ranked using wilson scoring interval
* added comments paging functionality (using "Load n more comments" links)
