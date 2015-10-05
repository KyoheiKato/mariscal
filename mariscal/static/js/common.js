$(function() {
    var $goodButton = $('.btn-good');
    var $badButton = $('.btn-bad');
    var $tweetButton = $('.btn-tweet');
    $goodButton.on('click', function() {
        var $select = $(this);
        valueAjax($(this)).done(function(result) {
            if (result['state']) {
                $select.addClass('good-active');
                $select.attr('data-state', 'active');
            } else {
                $select.removeClass('good-active');
                $select.removeAttr('data-state');
            }
            $select.find('span.user-number').text(result['number']);
        });
    });
    $badButton.on('click', function () {
        var $select = $(this);
        valueAjax($(this)).done(function(result) {
            if (result['state']) {
                $select.addClass('bad-active');
                $select.attr('data-state', 'active');
            } else {
                $select.removeClass('bad-active');
                $select.removeAttr('data-state');
            }
            $select.find('span.user-number').text(result['number']);
        })
    });
    $tweetButton.on('click', function() {
        tweetAjax($tweetButton).done(function(result) {
            if (result == 'OK') window.alert('ツイートしました。')
        })
    });
});

var valueAjax = function($valueButton) {
    return $.ajax({
        url: '/ajax/evaluate',
        type: 'POST',
        dataType: 'json',
        data: {
            mock: $valueButton.attr('data-mock'),
            user: $valueButton.attr('data-user'),
            state: $valueButton.attr('data-state')
        }
    })
};

var tweetAjax = function($tweetButton) {
    return $.ajax({
        url: '/ajax/tweet',
        type: 'POST',
        data: {
            text: $tweetButton.attr('data-value')
        }
    })
};