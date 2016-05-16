===============
Getting Started
===============

Installation
=============

Install a stable from PyPI using ``pip``::

    $ pip install django-notify-x

Install latest commit from Github::

    $ pip install -e git+git://github.com/v1k45/django-notify-x.git#egg=notify

Add ``notify`` in ``INSTALLED_APPS`` of your project settings::

    INSTALLED_APPS = (
        ...
        'notify',
        ...
    )

Include ``notify.urls`` in your ``urls.py`` with ``notifications`` as namespace::


    urlpatterns = [
        ...
        url(r'^notifications/', include('notify.urls', 'notifications')),
        ...
    ]


Finally, run migrations::

    $ python manage.py migrate notify


Dependencies
============

``django-notify-x`` currently supports Django 1.8 and above. There is no support for previous versions.
Both, Python 2.7 as well as Python 3.4 are supported.

It uses ``django-jsonfield`` package to add support to attach JSON data to notifications using the ``extra`` field.