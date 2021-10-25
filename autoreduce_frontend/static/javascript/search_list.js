function update_page(item) {
    let per_page = document.getElementById("select_per_page").value;
    document.location.href = document.location.href + "&per_page=" + per_page;
}

(function () {
    'use strict';

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var id = $(this).parents('[role="tablist"]').attr('id');
        var key = 'lastTag';
        if (id) {
            key += ':' + id;
        }

        localStorage.setItem(key, $(e.target).attr('href'));
    });

    $('[role="tablist"]').each(function (idx, elem) {
        var id = $(elem).attr('id');
        var key = 'lastTag';
        if (id) {
            key += ':' + id;
        }

        var lastTab = localStorage.getItem(key);
        if (lastTab) {
            $('[href="' + lastTab + '"]').tab('show');
        }
    });
})();