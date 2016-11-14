var markAllSuccess = function (response) {
    //console.log(response);
    // console.log(response.action);
    if (response.action == 'read') {
        var mkClass = readNotificationClass;
        var rmClass = unreadNotificationClass;
        $(nfSelector).css({'color': '#e0e0e0'});
        $(markNotificationSelector).css({'color': '#e0e0e0'});
        $(markLinkNotificationSelector).css({'opacity': '0.6'});
    } else {
        mkClass = unreadNotificationClass;
        rmClass = readNotificationClass;
        $(nfSelector).css({'color': '#000'});
        $(markNotificationSelector).css({'color': '#000'});
        $(markLinkNotificationSelector).css({'opacity': '1'});
    }
    // console.log(mkClass);
    // console.log(rmClass);
    $(nfSelector).removeClass(rmClass).addClass(mkClass);

    if (response.status === 200) {
      var notificationChange = response.responses.reduce(function(total, x) {
        return x.status === 200 ? total + 1 : total
      }, 0)
      if (response.action == 'read') {
        $('.notification-badge').each(function() {
          notificationCount = parseInt($(this).text()) - notificationChange;
          $(this).text(notificationCount);
        });
      } else {
        $('.notification-badge').each(function() {
          notificationCount = parseInt($(this).text()) + notificationChange;
          $(this).text(notificationCount);
        });
      }
    }
};
