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
     If you're going to use live ajax notifications and you have a notification box to display instant notifications on your project, you need to create one more file which starts with the corressponding ``nf_type`` and ends with ``_box.html``.


For example, if you have notifications with ``nf_type`` set to ``followed_user``, you'll create two files in your ``notifications/includes/`` directory of your template directory.

**The name of the files will be**::
    
    followed_user.html
    followed_user_box.html

.. note::
    Even if the names seem to be same, there are some differences you need to be careful about. Have a look at the example templates below.


**Contents of ``notifications/includes/followed_user.html``**::

    <!-- this format is not compulsory, you can have HTML that suits your project -->    
    <li data-nf-id="{{ notification.id }}"
    class="notification list-group-item {{ notification.read|yesno:'read,unread' }}">
        <a href="{{ notification.actor_url }}">{{ notification.actor }}</a> {{ notification.verb }}
        <span class="timesince">{{ notification.created|timesince }} ago</span>

        <button data-id="{{ notification.id }}" class="mark-notification"
            data-mark-action="{{ notification.read|yesno:'unread,read' }}">

            Mark as {{ notification.read|yesno:'unread,read' }}

        </button>
        <button class="delete-notification" data-id="{{ notification.id }}">X</button>
    </li>

**Contents of ``notifications/includes/followed_user_box.html``**::

    <!-- this format is not compulsory, you can have HTML that suits your project -->    
    <li data-nf-id="{{ notification_id }}"
    class="notification-box list-group-item {{ read|yesno:'read,unread' }}">
        
        <a href="{{ actor_url }}">{{ actor }}</a> {{ verb }}
        
        <span class="timesince">{{ created|timesince }}</span>
        
        <button data-id="{{ notification_id }}" class="mark-notification"
                data-mark-action="{{ read|yesno:'unread,read' }}">
            Mark as {{ read|yesno:'unread,read' }}
        </button>

        <button class="delete-notification" data-id="{{ notification_id }}">X</button>
    </li>

Apart from the formatting of HTML elements, there are some differences you need to take care of.

**They are**:

    - Template1 renders notification context using ``notification.`` as a variable prefix. It is nothing but the dictornary key.
    - Template2, however, renders notification context without an explicit ``notification.`` dictonary key.
    - The way of rendering ``notification ID`` is different in both.
        - Template 1 calls ``{{ notification.id }}``
        - Template 2 calls ``{{ notification_id }}``
        - **They can be easily mistaken**.

This is because the normal template takes ``notification`` as context from the QuerySet, where as the template used on the notification box takes context from ``.as_json()`` method of the model instance. This serializes the notification object as a JSON data without a parent key, thus all values are called directly.

Things to take care when writing notification templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Other than what we just discussed above, we need to make sure we do the following things correctly inorder to make this app work. These things are mostly the html attribute values will will be used by the javascript file inorder to perform DOM manipulation/

data-nf-id
    Attribute assigned to the parent element of notification. This will help our javascript to correctly select the parent notification element.

data-mark-action & data-id
    Attribute assigned to an element which will handle the control for marking a notification as read or unread.
    ``data-mark-action`` will also be used when marking all notifications as read or unread.

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

    .. warning::
        Make sure you include the js variables and the static file only when the user is authenticated. Inserting the scripts without authentication will send notification update request on the server. The notifications update view will redirect the request to login page when the request is un authenticated, so countless requests will be sent for nothing. 