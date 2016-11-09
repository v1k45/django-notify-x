====================
The client-side flow
====================

All the `views <modules/views.html>`__ of ``django-notify-x`` are compatible with both, AJAX and non-AJAX requests. The included javascript file helps you control the result of actions performed by user. Common tasks like making notifications fade out, changing background color when a notification is mark as read/ unread are already handled by default javascript functions.

Of course, you want things to appear differently for your project, for doing so, you can simply write your own version of the javascript functions and save them in the corresponding templates diretory of app and the things will get overridden easily.

To utilize read-only notifications or unread-only notifications, where the notification status is not toggled but set to read or unread respectively the list selector attribute class needs to be set to ``.read-notifications`` or ``.unread-notifications``. By default the included template will set the ``ul`` element class to ``.notifications`` which results in the toggle of read/unread. You can create your own ``all.html`` template or use javascript to modify the class selector on the client side.

The contents of default javascript function-files may seem to be useless, may be they are. But the files are just to give you idea about how things are supposed to work.

.. seealso::
    You might want to have a look on `Important HTML attributes <templates.html#things-to-take-care-when-writing-notification-templates>`__ of a notification templates. They'll play an important role in AJAX an DOM manipuation of notifications.

How notifications are updated
-----------------------------

The `notification_update <modules/views.html#notify.views.notification_update>`__ view explains the total flow of notification update requests.

The AJAX requests for updation of notifications are fired in every 5 seconds by default. You can control the time interval between the update requests by adding an entry named ``NOTIFY_UPDATE_TIME_INTERVAL`` set you the number of milliseconds you want.
