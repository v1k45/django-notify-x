============================
django-notify-x: quick guide
============================

.. image:: https://readthedocs.org/projects/django-notify-x/badge/?version=latest
   :target: http://django-notify-x.readthedocs.org/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://badge.fury.io/py/django-notify-x.svg
   :target: https://badge.fury.io/py/django-notify-x

.. image:: https://travis-ci.org/v1k45/django-notify-x.svg
   :target: https://travis-ci.org/v1k45/django-notify-x


Django NotifyX is a reusable app which adds notification system features to your Django app.

It was inspired from `django-notifications`_ , major differences include:
    - Multipe user notification at once.
    - A different approch for notification updates.
    - Less hassles when trying to format notifications differently accoring to their types.
    - AJAX support for everything.
    - And many more.

This is just a quick guide to get things to work ASAP. To dive into the details.. `Read the docs`_

How to install
==============

Downloading the package
-----------------------

Probably the best way to install is by using `PIP`::

    $ pip install django-notify-x

If you want to stay on the bleeding edge of the app::

    $ git clone https://github.com/v1k45/django-notify-x.git
    $ cd django-notify-x
    $ python setup.py install

Installing it on your project
-----------------------------

After the you've installed ``django-notify-x`` in your python enviroment. You have to make an entry of the same in your project ``settings.py`` file::

    INSTALLED_APPS = (
        ...
        'your.other.apps',
        ...
        'notify'.
    )

Then an entry on the ``urls.py`` file::

    urlpatterns = (
        url(r'^notifications/', include('notify.urls', 'notifications')),
    )

Then run migrations::

    $ python manage.py migrate notify

Then ``collectstatic`` to make sure you've copied the JS file for AJAX functionality::

    $ python manage.py collectstatic

You've successfully installed ``django-notify-x``!

Sending notifications
=====================

Sending notifications to single user
------------------------------------

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


Easy as pie, isn't it?

Sending notifications to to multiple users:
-------------------------------------------

.. code-block:: python

    from notify.signals import notify

    # your example view
    def upload_video(request):
        ...
        uploadvideo...
        ...
        video = VideoUploader.getupload()
        followers = list(request.user.followers())

        notify.send(request.user, recipient_list=followers, actor=request.user
                    verb='uploaded.', target=video, nf_type='video_upload_from_following')

        return YourResponse

Just change the ``recipient`` to ``recipient_list`` and send notifications to as many users you want!

.. warning::
     ``recipient_list`` expects supplied object to be a list() instance, make sure you convert your ``QuerySet`` to list() before assigning vaule.

Notification Template tags
==========================

This app comes with two notification tags, one renders notifications for you and the other includes javascript variables and functions relating the ``notifyX.js`` file.

render_notifications
--------------------

    As its name reflects, it will render notifications for you. ``render_notifications`` will take at least one parameter and maximum two parameters.

    You can use them to render notifications using a ``Notification`` QuerySet object, like this::

        {% load notification_tags %}
        {% render_notifications using request.user.notifications.active %}

    By default, the above tag will render notifications on the notifications page and not on the notification box. So it will use a template corresponing to it's ``nf_type`` with a ``.htm`` suffix nothing more.

    To render notificatons on a notifications box::
        
        {% load notification_tags %}
        {% render_notifications using request.user.notifications.active for box %}

    This tag will look for template name with ``_box.html`` suffixed when rendering notification contents.

    The ``request.user.notifications.active`` is just used to show an example of notification queryset, you can use any other way to supply a QuerySet of your choice.

include_notify_js_variables
---------------------------

    This tag uses ``notifications/includes/js_variables.html`` to include a template populated with JS variables and functions. You can override the values of any JS variables by creating your own version of ``js_variables.html`` template.

    To include JS variables for AJAX notification support, do this::

        {% load notification_tags %}
        {% if user.is_authenticated %}
            {% include_notify_js_variables %}
        {% endif %}

    This template inclusion includes three javascript files from the template includes directory, they are::

        mark_success.js
        mark_all_success.js
        delete_success.js
        update_success.js

    All of them are nothing but javascript function declarations which are supposed to run when a JQuery AJAX request is successfully completed.

And other things...
===================

It will be best to `Read the Docs`_ instead of expecting every thing from a quick guide :)


.. _django-notifications: https://www.github.com/django-notifications/django-notifications/
.. _Read the docs: http://django-notify-x.readthedocs.org/en/latest/index.html
