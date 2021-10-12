(function () {
    function setProgressCursor(elem) {
        elem.css('cursor', 'progress');
        $('body').css('cursor', 'progress');
    }

    function setDefaultCursor(elem) {
        elem.css('cursor', '');
        $('body').css('cursor', '');
    }

    let init = function init() {
        document.addEventListener("DOMContentLoaded", function () {
            setDefaultCursor($(this));
        });

        let select = document.getElementById('filter_select');
        if (select !== null) {
            select.onchange = function () {
                setProgressCursor($(this));
                document.getElementById('filter_options');
            };
        }

        let apply = document.getElementById('apply_filters');
        if (apply !== null) {
            apply.onclick = function () {
                setProgressCursor($(this));
            };
        }
    };

    init();
}())

function changePage(page) {
    let paginationChoice = document.getElementById("id_pagination").value;
    let filterChoice = document.getElementById("id_filter").value;
    let sortChoice = document.getElementById("id_sort").value
    document.location.href = window.location.origin + window.location.pathname + '?page=' + arguments[0] + '&filter=' + filterChoice + '&pagination=' + paginationChoice + '&sort=' + sortChoice;
}