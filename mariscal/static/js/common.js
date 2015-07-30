$(function() {
    var $goodButton = $('.btn-good');
    var $badButton = $('.btn-bad');
    $goodButton.on('click', function() {
        valueAjax($goodButton).done(function (result) {
            console.log(result);
            if (result['state']) {
                $goodButton.attr('class', 'good-active');
                $goodButton.attr('data-state', 'active');
            } else {
                $goodButton.removeAttr('class');
                $goodButton.attr('data-state', 'deactive');
            }
            $goodButton.find('span.user-number').text(result['number']);
        });
    });
    $badButton.on('click', function () {
        valueAjax($badButton).done(function (result) {
            if (result['state']) {
                $badButton.attr('class', 'bad-active');
                $badButton.attr('data-state', 'active');
            } else {
                $badButton.removeAttr('class');
                $badButton.attr('data-state', 'deactive');
            }
            $badButton.find('span.user-number').text(result['number']);
        })
    })
});

var valueAjax = function($valueButton) {
    return $.ajax({
        url: '/',
        type: 'POST',
        dataType: 'json',
        data: {
            mock: $valueButton.attr('data-mock'),
            user: $valueButton.attr('data-user'),
            state: $valueButton.attr('data-state'),
            value: $valueButton.attr('data-value')
        }
    })
};
