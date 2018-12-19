/**
 * Created by Roman on 11-Jun-17.
 */

window.topicFuncs = {
    deleteTopic: function () {
        if (confirm('This will permanently delete this topic and all related threads')) {
            window.util.postRedirect(window.TOPIC_URLS.deleteTopic);
        }
    }
};
