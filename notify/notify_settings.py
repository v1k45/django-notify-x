from django.conf import settings

# Class-selector of notification lists
NF_LIST_CLASS_SELECTOR = getattr(settings, 'NOTIFY_NF_LIST_CLASS_SELECTOR',
                                 '.notifications')

# Class-selector of mark read only notification lists
NF_READ_ONLY_LIST_CLASS_SELECTOR = getattr(settings, 'NOTIFY_NF_READ_ONLY_LIST_CLASS_SELECTOR', '.read-notifications')

# Class-selector of mark unread only notification lists
NF_UNREAD_ONLY_LIST_CLASS_SELECTOR = getattr(settings, 'NOTIFY_NF_READ_ONLY_LIST_CLASS_SELECTOR', '.unread-notifications')

# Class-selector for individual notifications.
SINGLE_NF_CLASS_SELECTOR = getattr(settings, 'NOTIFY_SINGLE_NF_CLASS_SELECTOR',
                                   '.notification')

# Class-selector for notification list on notification box.
NF_BOX_CLASS_SELECTOR = getattr(settings, 'NOTIFY_NF_BOX_CLASS_SELECTOR',
                                '.notification-box-list')

# Class-selector for individual notification in the notification box.
SINGLE_NF_BOX_CLASS_SELECTOR = getattr(settings,
                                       'NOTIFY_SINGLE_NF_BOX_CLASS_SELECTOR',
                                       '.notification-box')

# Class-selector for element performing `mark` as read/unread action.
MARK_NF_CLASS_SELECTOR = getattr(settings, 'NOTIFY_MARK_NF_CLASS_SELECTOR',
                                 '.mark-notification')

# Class-selector for link element to change opacity on `mark` as read/unread action.
MARK_NF_LINK_CLASS_SELECTOR = getattr(settings, 'NOTIFY_NF_LINK_CLASS_SELECTOR', '.mark-link-notification')

# Class-selector for element performing `mark_all` as read/unread action.
MARK_ALL_NF_CLASS_SELECTOR = getattr(settings,
                                     'NOTIFY_MARK_ALL_NF_CLASS_SELECTOR',
                                     '.mark-all-notifications')

# Class of notification element when it's status is read.
READ_NF_CLASS = getattr(settings, 'NOTIFY_READ_NOTIFICATION_CSS', 'read')

# Class of notification element when it's status is unread.
UNREAD_NF_CLASS = getattr(settings, 'NOTIFY_UNREAD_NOTIFICATION_CSS', 'unread')

# Class-selector for element performing `delete` action.
DELETE_NF_CLASS_SELECTOR = getattr(settings, 'NOTIFY_DELETE_NF_CLASS_SELECTOR',
                                   '.delete-notification')

# The tests fails if SOFT_DELETE setting is fetched from this file.
# Ref: https://code.djangoproject.com/ticket/22071
# TODO: Find a solution that passes the tests.
# # Whether do delete notifications softly or not.
# SOFT_DELETE = getattr(settings, 'NOTIFY_SOFT_DELETE', True)


# Time interval between ajax calls for notification update.
UPDATE_TIME_INTERVAL = getattr(settings, 'NOTIFY_UPDATE_TIME_INTERVAL', 5000)

# Page size for pagination
PAGE_SIZE = getattr(settings, 'NOTIFY_PAGE_SIZE', 20)
