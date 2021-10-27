(function () {

    var toggleInstrument = function toggleInstrument(event) {
        var $form = $(event.currentTarget.nextElementSibling);
        var $current_target = $(event.currentTarget);
        $("body").css("cursor", "wait");
        $current_target.css("cursor", "wait");
        event.stopImmediatePropagation();
        $.ajax({
            url: $form.attr('action'),
            type: "POST",
            data: $form.serialize(),
            success: function (data) {
                $form.find("#currently_paused").val(data["currently_paused"]);
                var currently_paused = (data["currently_paused"].toLowerCase() == "true");

                $current_target.toggleClass("btn-success btn-danger");

                if (currently_paused) {
                    $current_target.html($current_target.html().replace("Pause", "Resume"));
                    $current_target.find('svg').addClass('fa-play').removeClass('fa-pause').attr('data-icon', 'play');
                } else {
                    $current_target.html($current_target.html().replace("Resume", "Pause"));
                    $current_target.find('svg').addClass('fa-pause').removeClass('fa-play').attr('data-icon', 'pause');
                };

                $("body").css("cursor", "default");
                $current_target.css("cursor", "pointer");
            }
        })
    };

    var init = function init() {
        $("[id^='pause']").on('click', toggleInstrument);
    };

    init();
}());