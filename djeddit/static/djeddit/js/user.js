/**
 * Created by Roman on 10-Jun-17.
 */

window.userFuncs = {
    setUserStatus: function (username, status) {
        var url = window.util.getAbsoluteURL('set_user_status');
        $.post(url, {username: username, status: status});
    }
};