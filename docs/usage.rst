===================
Using Django Notify
===================

This page will describe how to use ``django-notify-x``.

Component details
=================

Just like ``django-notifications``, this app also follows the approach described by `ActivityStrea.ms`_ . Notifications are generated when an action is performed on concerning a recipient.

The following are the main components:

    - **Actor**: The object which performed the activity.
    - **Verb**: The activity.
    - **Object**: The object on which activity was performed.
    - **Target**: The object where activity was performed.

These parameters are nothing but ``GenericForeignKey`` relation to an arbitrary Django model object.

The parameters **Action Object** and **Target** can be left optional. Even **Actor** in somecases can be said as optional, there can be many cases for this. Therefore, all parameters can have *Anonymous* objects, not objects actually, but texts.

All three parameters, *Actor, Action Object and, Target* have their respective fields where the object property can be left empty and a simple text value can be used instead.

.. _`ActivityStrea.ms`: http://activitystrea.ms/specs/atom/1.0/

Example notification cases
==========================

    - **John** followed you. XX minutes ago.
        - ``<actor> <verb> <created>``
    - **Jane** commented on your post *Django is fun*. XX minutes ago.
        - ``<actor> <verb> <target> <created>``
    - **John** replied on your *comment* on *Django is fun*.  XX minutes ago.
        - ``<actor> <verb> <object> <target> <created>``
    - **You** received 20 points. Today.
        - ``<actor_text> <verb> <created>``
    - *and many more...*


Sending Notifications
=====================

Sending notifications to single user
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
     ``recipient_list`` expects supplied object to be a ``list()`` or ``set()`` instance, make sure you convert your ``QuerySet`` to ``set()`` or ``list()`` before assigning value. ``set()`` is preferred because it eliminates duplicate values and membership checks are faster.
