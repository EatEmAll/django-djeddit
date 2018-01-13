/**
 * Created by Roman on 11-Jun-17.
 */

window.topicFuncs = {
  deleteTopic: function (topic_title) {
    if (confirm('This will permanently delete this topic and all related threads')) {
        window.location = window.TOPIC_URLS['deleteTopic'];
    }
  }
};
