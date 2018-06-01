/**
 * Created by Roman on 10-Jun-17.
 */

window.userFuncs = {
    setUserStatus: function (username, status) {
        var url = window.USER_URLS['setUserStatus'];
        $.post(url, {username: username, status: status});
    }
};
