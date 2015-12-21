var markAllSuccess = function (response) {
    //console.log(response);
    // console.log(response.action);
    if (response.action == 'read') {
        var mkClass = readNotificationClass;
        var rmClass = unreadNotificationClass;
    } else {
        mkClass = unreadNotificationClass;
        rmClass = readNotificationClass;
    }
    // console.log(mkClass);
    // console.log(rmClass);
    $(nfSelector).removeClass(rmClass).addClass(mkClass);
};
