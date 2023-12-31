$(document).ready(function () {
    // this is the id of the form
    $("#search_form").submit(function (e) {
        e.preventDefault(); // avoid to execute the actual submit of the form.

        var form = $(this);
        var url = form.attr('action');

        $.ajax({
            type: "POST",
            url: url,
            data: form.serialize(), // serializes the form's elements.
            headers: { 'X-CSRFToken': form.attr('csrf_token') },
            success: function (data) {
                document.getElementById("entry_table").innerHTML = data;
            }
        });
    });
    // trigger submit to get the initial table of entries:
    $("#search_form").submit();
});
