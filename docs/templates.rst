==========================
Notification and templates
==========================

Django's templating system plays a very important role in formatting your notifications without hassles. The templates for ``django-notify-x`` app are supposed to be stored in ``notifications`` directory of your default template directory.

As explained in previous chapter, ``django-notify-x`` uses templates to format different kinds of notifications corresponding to the ``nf_type`` of the notification.

Templates for notification types
================================

If you want to render notifications using the ``render_notifications`` template tag and want to distingush notifications by their output locations (for example, *a typical web app has a notification page as well as a notification-box in it's navigation bar*.) you can use templates to store HTML format data for different kind of notifications.

The templates for notifications are stored in ``notifications`` directory of templates folder.

The tree structure representation of template directory
::
    templates
    |-- base.html
    `-- notifications
        |-- all.html
        |-- base.html
        `-- includes
            |-- default_box.html
            |-- default.html
            |-- delete_success.js
            |-- js_variables.html
            |-- mark_all_success.js
            |-- mark_success.js
            |-- navbar.html
            `-- update_success.js

The ``includes`` sub-directory is for storing HTML output template for individual notifications and also Javascript files corresponding to the functions in the ``notifyX.js`` file.

For rendering notifications
---------------------------

The ``all.html`` and ``base.html`` under ``notifications`` directory are used when rendering the `all notifications page`. You can override both of them by creating them on your default template directory under ``notifications`` sub-directory.

For formatting notification
---------------------------

HTML output format for individual notifications are supposed to be stored in ``notifications/includes/`` with the name of their ``nf_type`` ending with a ``.html``.

.. note::
     If you're going to use live ajax notifications and you have a notification box to display instant notifications on your project, you might want to create one more file which starts with the corressponding ``nf_type`` and ends with ``_box.html`` in order to use different formatting.


For example, if you have notifications with ``nf_type`` set to ``followed_user``, the name of the custom template files will be::

    followed_user.html
    followed_user_box.html

Put those files in ``notifications/includes/`` directory of your template directory.

For full page notifications, we'll try to find a template in the following order::

    followed_user.html
    defaul.html

For live ajax notifications, we'll try to find a template in the following order::

    followed_user_box.html
    followed_user.html
    default_box.html


**Contents of `notifications/includes/followed_user.html`**::

    <!-- this format is not compulsory, you can have HTML that suits your project -->
    <li data-nf-id="{{ notification.id }}"
    class="notification list-group-item {{ notification.read|yesno:'read,unread' }}">
        <a href="{{ notification.actor_url }}">{{ notification.actor }}</a> {{ notification.verb }}
        <span class="timesince">{{ notification.created|timesince }} ago</span>

        <button data-id="{{ notification.id }}" class="mark-notification"
            data-mark-action="{{ notification.read|yesno:'unread,read' }}"
            data-toggle-text="Mark as {{ notification.read|yesno:_('read,unread') }}">

            Mark as {{ notification.read|yesno:'unread,read' }}

        </button>
        <button class="delete-notification" data-id="{{ notification.id }}">X</button>
    </li>

**Contents of `notifications/includes/followed_user_box.html`**::

    <!-- this format is not compulsory, you can have HTML that suits your project -->
    <li data-nf-id="{{ notification.id }}"
    class="notification list-group-item {{ notification.read|yesno:'read,unread' }}">
        <a href="{{ notification.actor_url }}">{{ notification.actor }}</a> {{ notification.verb }}
        <span class="timesince">{{ notification.created|timesince }} ago</span>

        <button data-id="{{ notification.id }}" class="mark-notification"
            data-mark-action="{{ notification.read|yesno:'unread,read' }}"
            data-toggle-text="Mark as {{ notification.read|yesno:_('read,unread') }}">

            Mark as {{ notification.read|yesno:'unread,read' }}

        </button>
        <button class="delete-notification" data-id="{{ notification.id }}">X</button>
    </li>

.. note::
    The contents of the examples above are identical, in this case you might create only the `followed_user.html` file.


Things to take care when writing notification templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Other than what we just discussed above, we need to make sure we do the following things correctly inorder to make this app work. These things are mostly the html attribute values will will be used by the javascript file inorder to perform DOM manipulation/

data-nf-id
    Attribute assigned to the parent element of notification. This will help our javascript to correctly select the parent notification element.

data-mark-action & data-id
    Attribute assigned to an element which will handle the control for marking a notification as read or unread.
    ``data-mark-action`` will also be used when marking all notifications as read or unread.

data-mark-action & data-toggle-text
    The element that holds the attribute ``data-mark-action`` will have it's innerHTML text replaced to reflect the toggle behavior.
    In order to customize the toggled text, you should provide the opposite text into a ``data-toggle-text`` attribute.

delete-notification & data-id
    Attribute assigned to an element which handles deleting of a notification.

.. note::
    The above settings are only necessary if you want things happen over AJAX. If you want to control things with POST request, there is absolutely no need of keeping these attributes.


Notification Template tags
==========================

This app comes with two notification tags, one renders notifications for you and the other includes javascript variables and functions relating the ``notifyX.js`` file.

render_notifications
--------------------

    As its name reflects, it will render notifications for you. ``render_notifications`` will take at least one parameter and maximum two parameters.

    You can use them to render notifications using a ``Notification`` QuerySet object, like this::

        {% load notification_tags %}
        {% render_notifications using request.user.notifications.active %}

    By default, the above tag will render notifications on the notifications page and not on the notification box. So it will use a template corresponing to it's ``nf_type`` with a ``.html`` suffix nothing more.

    To render notificatons on a notifications box::

        {% load notification_tags %}
        {% render_notifications using request.user.notifications.active for box %}

    This tag will look for template name with ``_box.html`` suffixed when rendering notification contents.

    The ``request.user.notifications.active`` is just used to show an example of notification queryset, you can use any other way to supply a QuerySet of your choice.

    As each notification has many generic relations (actor, target, object),
    and the Django's default behavior when evaluating queries is to hit the
    database once per relation per record, the amount of queries to render many
    notifications can grow quickly. To handle this case, the ``Notification``
    queryset has a method ``prefetch``, that prefetches the relations and
    reduces the number of queries needed to ``N+Y``, where ``N`` is the number
    of notifications on the master queryset, and ``Y`` is the number of
    distinct models that your notifications refers to.

    Use ``prefetch`` as the last queryset method in the chain, as it will
    evaluate the queryset and prefetch all generic relations::

        {% load notification_tags %}
        {% render_notifications using request.user.notifications.active.prefetch %}


include_notify_js_variables
---------------------------

    This tag uses ``notifications/includes/js_variables.html`` to include a template populated with JS variables and functions. You can override the values of any JS variables by creating your own version of ``js_variables.html`` template.

    To include JS variables for AJAX notification support, do this::

        {% load notification_tags %}
        {% include_notify_js_variables %}

    This template inclusion includes four javascript files from the template includes directory, they are::

        mark_success.js
        mark_all_success.js
        delete_success.js
        update_success.js

    All of them are nothing but javascript function declarations which are supposed to run when a JQuery AJAX request is successfully completed.

    .. note::
        **Changed in version 0.1.1**

        In the previous versions, it was necessarty to add notification check before including the JS variables using the ``include_notify_js_variables`` template tag. It is no more required. The new update checks for authenticated users and then renders the tempalte if required.

user_notifications
------------------

    .. note::
        **Added in version 0.1.1**

        The ``user_notifications`` tag is a shortcut to the ``render_notifications`` tag. It directly renders the notifications of the logged-in user on the specified target.

    You can use this tag like this::

        {% load notification_tags %}
        {% user_notifications %}

    This tag renders active notifications of the user by using something like ``request.user.notifications.active()``.

    Just like ``render_notifications`` it also takes rendering target as an optional argument. You can specify rendering target like this::

        {% load notification_tags %}
        {% user_notifications for box %}

    By default, it'll use 'page' as the rendering target and use full page notification rending template corresponding to the ``nf_type`` of the template.
