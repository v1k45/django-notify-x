Changelog
=========

- Version 0.1.5
    - Custom rendering targets for notifications
    - ``raw_id_fields`` on admin for large user count 
    - Replaced ``UrlField`` with ``CharField``
    - Started using ``cached_property`` for better performace.
    - Minor bug fixes and improvements.
    - Updated on 27th March 2016

- Version 0.1.4
    - Generic relations are prefetched by default, saves queries ridiculously!
    - Bug fixes in template tag and notification update view.
    - Updated on 13th February 2016

- Version 0.1.3
    - Included the static files and templates were missing from PyPI package.
    - Added a view to mark notification as read and redirect to the target url.
    - Added info about concatenation support; fixed minor typos
    - Updated on 30th December 2015

- Version 0.1.2
    - Fernando added translation support for ``pt_BR``.
    - Bug fixes in the javascript file.
    - More roboust mechanism when performing read/unread actions on the client-side.
    - Consistent notification context.
    - Registered ``Notification`` Model in Admin Site.
    - Updated on 21st December 2015

- Version 0.1.1
    - Minor changes
    - Added ``user_notifications`` template tag.
    - Added check for authentication when including JS variables.
    - Updated on 18th December 2015

- Version 0.1
    - Initital Commit.
    - Features like mutiple user notify, anonymous activity stream components are supported.
    - Supports Django 1.8+ on both, python2.7 and python3.4
    - Released on 13th December 2015