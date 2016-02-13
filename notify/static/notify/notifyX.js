/**
 * django-notify-x.
 */

// Variable declaration;

// AJAX call URLs
var updateNotificationUrl;
var markNotificationUrl;
var markAllNotificationUrl;
var deleteNotificationUrl;

// Class selectors
var nfListClassSelector;
var nfClassSelector;
var nfBoxListClassSelector;
var nfBoxClassSelector;
var nfListSelector = nfBoxListClassSelector + ", " + nfListClassSelector;
var nfSelector = nfClassSelector + ", " + nfBoxClassSelector;

var markNotificationSelector;
var markAllNotificationSelector;
var deleteNotificationSelector;

// Class details
var readNotificationClass;
var unreadNotificationClass;

// Ajax success functions.
var markSuccess;
var markAllSuccess;
var deleteSuccess;
var updateSuccess;

var notificationUpdateTimeInterval;

// Django's implementation for AJAX-CSRF protection.
// https://docs.djangoproject.com/en/dev/ref/csrf/#ajax
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// CSRF Implementation End.

// Mark a notification as read/unread using AJAX.
$(document).ready(function () {
    $(nfListSelector).delegate(markNotificationSelector, 'click', function () {

        var $notification = $(this);
        var mark_action = $notification.attr('data-mark-action');
        var mark_post_data = {
            id: $notification.attr('data-id'),
            action: mark_action,
            csrftoken: csrftoken
        };

        $.ajax({
            type: 'POST',
            url: markNotificationUrl,
            data: mark_post_data,
            success: function (response) {
                //console.log(response);
                markSuccess(response, $notification);
            }
        });
    });
});

// Mark all notifications as read or unread using AJAX.
$(document).ready(function () {
    $(markAllNotificationSelector).on('click', function () {
    //$(nfListSelector).delegate(markAllNotificationSelector, 'click', function () {

        var mark_all_post_data = {
            action: $(this).attr('data-mark-action'),
            csrftoken: csrftoken
        };

        $.ajax({
            type: 'POST',
            url: markAllNotificationUrl,
            data: mark_all_post_data,
            success: function (response) {
                //console.log(response);
                markAllSuccess(response);
            }
        });
    });
});

// Delete a notification using AJAX.
$(document).ready(function () {

    //$(deleteNotificationSelector).on('click', function () {
    $(nfListSelector).delegate(deleteNotificationSelector, 'click', function () {

        var $notification = $(this);

        var delete_notification_data = {
            id: $notification.attr('data-id'),
            csrftoken: csrftoken
        };

        $.ajax({
            type: 'POST',
            url: deleteNotificationUrl,
            data: delete_notification_data,
            //success: deleteSuccess(response)
            success: function (response) {
                deleteSuccess(response, $notification);
            }
        });
    });
});

// Update a notification using AJAX.
$(document).ready(function updateNotifications() {
    var $notification_box = $(nfBoxListClassSelector);
    var flag = $notification_box.children().first().attr('data-nf-id') || '1';

    if (!flag || $notification_box.length == 0) {
        console.log('Notity improperly configured. No data-nf-id was found.')
        console.log('  Make sure you have a container element with \''+ nfBoxListClassSelector + '\' as css class.');
        return;
    }

    $.ajax({
        type: 'GET',
        url: updateNotificationUrl + '?flag=' + flag,
        //success: updateSuccess(response),
        success: function (response) {
            //console.log('update received');
            updateSuccess(response);
        },
        complete: function () {
            setTimeout(updateNotifications, notificationUpdateTimeInterval);
        }
    });
});
