=====================================
Understanding Notification Attributes
=====================================

This is a detailed walk through the functioning of ``django-notify-x``. This page will describe the use of Notification Model fields and the ``notify`` signal, so that you can make the most out of it.

Important fields in Notification Model
======================================

Anonymous values:
-----------------

    - Each activity stream component can carry an anonymous value instead of being a model object.
    - You can also specify the its URL as text. By default ``get_absolute_url()`` method is called to assign a URL to activitiy stream participator.
    - At Django Model level inserts, the field name of these components are as follows:
        - ``actor_content_object``: For directly populating the model using a model instance.
        - ``actor_content_type``: For manually assinging the object's content_type.
        - ``actor_object_id``: ID of the object for manual assignment.
        - ``actor_text``: Name of the actor in plain text (useful when using anonymous actor).
        - ``actor_url_text``: URL of the actor in plain text (useful when using anonymous actor).
        - ... the same goes for **target and obj** components of activity stream.


Notification types:
-------------------

    - Each notification is different, they must be formatted differently during HTML rendering. For this, each notification gets to carry its own notification type.

    - This notification type will be used to search the special template for the notification located at ``notifications/includes/NF_TYPE.html`` of your template directory.

    - The main reason to add this field is to save you from the pain of writing ``if...elif...else`` blocks in your template file just for handling how notifications will get rendered.

    - With this, you can just save template for an individual notification type and call the *template-tag* to render all notifications for you without writing a single ``if...elif...else`` block.

    - You’ll just need to do a ``{% render_notifications using NOTIFICATION_OBJ %}`` and you’ll get your notifications rendered.

    - By default, every ``nf_type`` is set to ``default``.

The shortcut properties for activity components:
------------------------------------------------

    - Every activity component has its property which returns either the `__str__` value of ``ACTIVITY-COMPONENT_content_object`` or the value of its anonymous text or ``None``.

        - For example::

            notification = Notification.objects.get(pk=1)

            # Instead of doing this
            if notification.actor_content_object:
                actor_value = notification.actor_content_object
            elif notification.actor_text:
                actor_value = notification.actor_text
            else:
                actor_value = 'fallback text'

            # you can do this
            notification.actor

    - The same way, every activity component is supposed contain a URL which is either the model object's ``get_absolute_url()`` value or ``ACTIVITYCOMPONENT_url_text`` or ``None`` or a fallback value.

        - You guessed it right!, There's a property for this thing too.
        - You can just access the activity component's URL like ``notification.actor_url``.
        - ``notification.actor_url`` will either return the URL using the above methods or just return a ``"#"`` as a fallback URL.

    - Not a property, but a model method...

        ``.as_json()``, converts the values of the model instance to JSON or python dictonary, it is used when sending live notification updates as JSON format.


Other fields:
-------------

verb
^^^^
    Carries the verb of the notification performed.

description
^^^^^^^^^^^
    Carries *optional* text description of the notification.

extra
^^^^^
    JsonField, allows arbirary values in JSON format, so that you can store other useful information about a specific notification.

deleted
^^^^^^^
    Useful when you want to *soft delete* notifications instead of diretly deleting them from database.
    The nature of this attribute can be controlled by a setting ``NOTIFY_SOFT_DELETE = False``. This will delete notifications directly from database. By default, notifications are soft-deleted.

Important options in notify method
==================================

The keyword arguments when sending a ``notify`` signal are quite different than that of the Notification Model. Some fields are skipped and some are renamed for convenience. The below is the overview of the significant changes you need to know.

The actor, target and obj components
------------------------------------

    The ``actor`` keyword argument acts as ``actor_content_object`` at Django model level insert.
    There is not explicit *kwarg* for ``actor_content_type`` and ``actor_object_id``.
    Same goes for ``target`` and ``obj``.


The recipient and recipient_list
--------------------------------

    The ``notify`` signal takes these two as conditionally optional keyword arguments. They can neither be supplied together nor be empty. The ``recipient`` takes a user model instance only, the same case is with the ``recipient_list`` which takes a ``list()`` or ``set()`` of user model instances. A ``set()`` is preferred
    because it will only contain unique elements and eliminate duplicate notification checks and membership checks on a set are faster.

    They're accessible from single signal because it would be highly redundant to create a separate signal with almost identical parameters just for the sake of making things distinguishable.


The first positional argument
-----------------------------

    When sending a notification, the first arument stands for the ``sender`` of the signal. For most cases it will be your ``User`` model. You can either user a user instance or the model class itself as the first parameter.
