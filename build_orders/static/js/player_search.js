$(function() {
    $.get('player_list',
        function(data) {
            $('.typeahead').typeahead({
                source: data.players,
            });
        });
});
