/**
 * Created by Roman on 06-Feb-17.
 */

window.util = {
  getAbsoluteURL: function (url) {
      var absoluteURL = new URL(url, window.BASE_URL);
      return absoluteURL.href;
  },
  toggleForm: function(url, $placeAfter, params, $toggle, onSuccessFunc) {
    if ($toggle === undefined || !$toggle.hasClass('clicked')) {
        // load a form a given url
        $.get(url, params, function (data) {
            $placeAfter.after(data);
            if (typeof onSuccessFunc === 'function')
                onSuccessFunc();
        });
    }
    else // remove the form
        $placeAfter.next().remove();
    $toggle.toggleClass('clicked');
  }
};