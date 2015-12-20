======================
Further configurations
======================

After you've installed the app and made an entry in the ``INSTALLED_APPS`` of your project settings, there are things that you still need to know about.

If you are planning to handle things over AJAX, make sure you run this command before starting to hack the app::

    $ python manage.py collectstatic

This will copy ``notifyX.js`` and ``notifyX.min.js`` to your static root directory.

The ``notifyX.js`` file handles all the AJAX related actions ranging from marking notifications as read/unread to fetching new notifications and updating the notification box.

Now, include the ``notifyX.js`` static file in your base template.::

    {% load staticfiles %}
    ....
    <script src="{% static "notify/notifyX.js" %}"></script>
    <!-- OR -->
    <script src="{% static "notify/notifyX.min.js" %}"></script>


.. note::
    The other file, ``notifyX.min.js`` is a minified version of ``notifyX.js``. It is intended work the same as the original file. The advantage of a minified javascript file is that it removes unnecessary things and ultimately reduces the size of the final file with same functionality.

.. warning::
    Make sure you include ``notifyX.js`` after you've included latest JQuery javascript file. This script uses JQuery to handle AJAX calls and DOM manipulation. It will break if JQuery is not included before it.


Project level settings
======================

All the settings defined below will mostly be used when making AJAX calls and DOM manipulations. These settings will be supplied to `include_notify_js_variables <templates.html#include-notify-js-variables>`_ template tag for JS inclusion.

*The settings will be represented in the following way*

``PROJECT_LEVEL_SETTING`` (default value)
    Description for the project level setting.

``NOTIFY_SOFT_DELETE`` (True)
    Whether to do delete notifications softly or not.

``NOTIFY_NF_LIST_CLASS_SELECTOR`` (.notifications)
    Class selector of element containing list of notification elements.

``NOTIFY_SINGLE_NF_CLASS_SELECTOR`` (notifications)
    Class selector of individual notification elements.

``NOTIFY_NF_BOX_CLASS_SELECTOR`` (.notification-box-list)
    Class selector of element containing list of notification elements on *notification box*.

``NOTIFY_SINGLE_NF_BOX_CLASS_SELECTOR`` (.notification-box)
    Class selector of individual *notification-box* elements.

``NOTIFY_MARK_NF_CLASS_SELECTOR`` (.mark-notification)
    Class selector for sub-element of notification element performing `mark` as read/unread action. This will be same for both, full page notifications as well as notification box on the navbar.

``NOTIFY_MARK_ALL_NF_CLASS_SELECTOR`` (.mark-all-notifications)
    Class selector for sub-element of notification element performing `mark_all` as read/unread action.

``NOTIFY_READ_NOTIFICATION_CSS`` (read)
    Class of parent notification element when its status is read.

``NOTIFY_UNREAD_NOTIFICATION_CSS`` (unread)
    Class of parent notification element when its status is unread.

``NOTIFY_DELETE_NF_CLASS_SELECTOR`` (.delete-notification)
    Class selector for sub-element of notification element performing `delete` action.

``NOTIFY_UPDATE_TIME_INTERVAL`` (5000)
    Time interval (in ms) between ajax calls for notification update.