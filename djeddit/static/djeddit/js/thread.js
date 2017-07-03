/**
 * Created by Roman on 12-Dec-16.
 */

window.postFuncs = {
    removePostForm: function (post) {
        $('#' + post + '>.bs-callout-main').next().remove();
    },
    togglePostForm: function (post, toggle, url) {
        url = window.util.getAbsoluteURL(url + post);
        var $placeAfter = $('#' + post + '>.bs-callout-main');
        window.util.toggleForm(url, $placeAfter, {}, $(toggle));
    },
    toggleEditForm: function (post, toggle, toggleHeader) {
        var $placeAfter = $('#' + post + '>.bs-callout-main');
        $placeAfter.toggle();
        this.togglePostForm(post, toggle, 'edit_post/');
        if (toggleHeader)
            $('.bs-callout-heading').toggle();
    },
    votePost: function (post, upvoted, downvoted) {
        var vote = 0;
        if (upvoted)
            vote += 1;
        if (downvoted)
            vote -= 1;
        var url = window.util.getAbsoluteURL('vote_post');
        var params = {post: post, vote: vote};
        $.post(url, params, function (data) {
            var $post = $('#' + post);
            // update arrow icons
            var $upvoteIcon = $post.find('>.bs-callout-main>.minicol>.glyphicon-chevron-up');
            var $downvoteIcon = $post.find('>.bs-callout-main>.minicol>.glyphicon-chevron-down');
            if (vote === 1)
                $upvoteIcon.addClass('color-primary');
            else
                $upvoteIcon.removeClass('color-primary');
            if (vote === -1)
                $downvoteIcon.addClass('color-primary');
            else
                $downvoteIcon.removeClass('color-primary');
            // update post's displayed score
            $post.find('>.post-heading>.post-score').text(data.scoreStr);
            $post.find('>.bs-callout-main>.minicol>.post-score').text(data.score);
        })
    },
    toggleReplies: function (post) {
        var $icon = $('#' + post + '>.post-heading>.fa.toggle-replies');
        $icon.toggleClass('fa-minus-square-o');
        $icon.toggleClass('fa-plus-square-o');
        $('>.bs-callout-main', '#' + post).slideToggle('fast');
        $('.post-container', '#' + post).slideToggle('fast');
    },
    deletePost: function (post, show_confirm) {
        if (!show_confirm || confirm('This will permanently delete this thread and all related comments'))
            window.location = window.util.getAbsoluteURL('delete_post/' + post);
    },
    getPostRepliesUids: function (post) {
        // get uids of shown replies to a given post
        var $baseElem = $('#comments-callout');
        if (post)
            $baseElem = $baseElem.find('#' + post);
        var $replies = $baseElem.find('.post-container');
        var $uids = $replies.map(function (i) {
            return $replies[i].id;
        });
        return $uids.toArray();
    },
    loadAdditionalReplies: function ($elem, post, op) {
        // load missing replies for a given post into $elem
        var excluded = this.getPostRepliesUids(post);
        var url = window.util.getAbsoluteURL('load_additional_replies');
        var params = {post: post ? post : op, excluded: JSON.stringify(excluded)};
        $.get(url, params, function (data) {
            $elem.replaceWith(data);
        });
    }
};
