============================
django-notify-x: quick guide
============================

.. image:: https://readthedocs.org/projects/django-notify-x/badge/?version=latest
   :target: http://django-notify-x.readthedocs.org/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://badge.fury.io/py/django-notify-x.svg
   :target: https://badge.fury.io/py/django-notify-x

.. image:: https://travis-ci.org/v1k45/django-notify-x.svg?branch=nf_concat_support
   :target: https://travis-ci.org/v1k45/django-notify-x


Django NotifyX is a reusable app which adds notification system features to your Django app.

It was inspired from `django-notifications`_ , major differences include:
    - Multipe user notification at once.
    - A different approach for notification updates.
    - Less hassles when trying to format notifications differently according to their types.
    - AJAX support for everything.
    - **Notification concatenation support!**
    - And many more.

This is just a quick guide to get things to work ASAP. To dive into the details.. `Read the docs`_

How to install
==============

Downloading the package
-----------------------

Download and install the package::

    $ git clone https://github.com/v1k45/django-notify-x.git
    $ cd django-notify-x
    $ git checkout nf_concat_support
    $ python setup.py install

Installing it on your project
-----------------------------

After the you've installed ``django-notify-x`` in your python enviroment. You have to make an entry of the same in your project ``settings.py`` file::

    INSTALLED_APPS = (
        ...
        'your.other.apps',
        ...
        'notify',
    )

Then an entry on the ``urls.py`` file::

    import notify

    urlpatterns = (
        url(r'^notifications/', include(notify.urls, 'notifications')),
    )

Then run migrations::

    $ python manage.py migrate notify

Then ``collectstatic`` to make sure you've copied the JS file for AJAX functionality::

    $ python manage.py collectstatic

You've successfully installed ``django-notify-x``!

Major Changes
=============

- Anonymous activity stream components are no longer supported.
- ``notify`` signal is renamed to ``notification`` because ``notify.send`` sounds weird (._.')
- AJAX notifications updates are done using a different flag.
    - It is nothing but the timestamp of last modification of notification.
    - The use of ID based flag wasn't possible as notifications are updated instead of created when a new actor does the exact same action.
    - Also, the HTML data attribute ``data-nf-id`` is changed to ``data-nf-flag``.
- You are no longer forced to convert recipient_list to ``list()``.

How to use
==========

Sending notifications to a single user:
---------------------------------------

.. code-block:: python

    from notify.signals import notify

    # your example view
    def follow_user(request, user):
        user = User.objects.get(username=user)
        ...
        dofollow
        ...

        notify.send(request.user, recipient=user, actor=request.user
                    verb='followed you.', nf_type='followed_by_one_user')

        return YourResponse


Just like you do on the stable branch.

Sending notifications to multiple users:
----------------------------------------

.. code-block:: python

    from notify.signals import notify

    # your example view
    def upload_video(request):
        ...
        uploadvideo...
        ...
        video = VideoUploader.getupload()
        followers = request.user.followers()

        notify.send(request.user, recipient_list=followers, actor=request.user
                    verb='uploaded.', target=video, nf_type='video_upload_from_following')

        return YourResponse

Yeah, nothing different.

How notification concatenation works:
-------------------------------------

- You just have to send the same notification (nf_type, target and recipient) with a different actor and the actor gets added in the actors list.

- When you call ``notification.actor`` property, it will return the str value of the first two actors followed by the number of actors.
    - It returns like:

        - *John did this action*
        - *John and Jane did this action*
        - *John, Jane and 24 others did this action*

- The ``actors`` is a generic M2M fields instead of ``GenericForeignKey``. This means that you can have as many actors you in a single notification.

IMPORTANT
=========
- This app works exactly the same as the stable version, the only differences are version support.

- **Currently, this app only supports Django 1.8.x on Python3.**. Support for Python2.7 will be soon added.

- This app uses *tkhyn*'s `django-gm2m <https://bitbucket.org/tkhyn/django-gm2m>`__. For some reasons, ``gm2m`` has no support for django 1.9 as of now. This is why there is no support for versions above 1.8 in django-notify-x.

- The tests for python27 are failing only for few methods, they'll be resolved ASAP :)

TODO List
=========

- Support python27 and django19
- Convert *Function based views* to *Class Based views*.

.. _django-notifications: https://www.github.com/django-notifications/django-notifications/
.. _Read the docs: http://django-notify-x.readthedocs.org/en/latest/index.html
