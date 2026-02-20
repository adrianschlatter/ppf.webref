$(document).ready(function () {
    var entryViewer = $("#entry_viewer");
    var entryViewerTitle = $("#entry_viewer_title");
    var entryViewerAuthors = $("#entry_viewer_authors");
    var entryViewerDate = $("#entry_viewer_date");
    var entryViewerType = $("#entry_viewer_type");
    var entryViewerCitationKey = $("#entry_viewer_citationkey");
    var entryViewerFiles = $("#entry_viewer_files");
    var selectedRow = null;

    function clearSelectedRow() {
        if (selectedRow) {
            selectedRow.removeClass("selected");
            selectedRow = null;
        }
    }

    function hideEntryViewer() {
        entryViewer.addClass("hidden");
        clearSelectedRow();
    }

    function renderFiles(files) {
        entryViewerFiles.empty();
        if (!files || files.length === 0) {
            return;
        }
        if (files.length === 1) {
            entryViewerFiles.append(
                $("<a>").attr("href", files[0].href).text(files[0].label)
            );
            return;
        }
        var select = $("<select>").attr("id", "entry_viewer_files_select");
        select.append($("<option>").attr("value", "").text("Select file"));
        files.forEach(function (file) {
            select.append(
                $("<option>").attr("value", file.href).text(file.label)
            );
        });
        select.on("change", function () {
            var href = $(this).val();
            if (href) {
                window.location = href;
                $(this).val("");
            }
        });
        entryViewerFiles.append(select);
    }

    function showEntryViewer(data) {
        entryViewerTitle.text(data.title || "");
        entryViewerAuthors.text(data.authors || "");
        entryViewerDate.text(data.date || "");
        entryViewerType.text(data.type || "");
        entryViewerCitationKey.text(data.citationkey || "");
        renderFiles(data.files || []);
        entryViewer.removeClass("hidden");
    }

    function bindEntryRows() {
        $(".entry-row").off("click").on("click", function (event) {
            if ($(event.target).is("a")) {
                return;
            }
            var sharedId = $(this).data("shared-id");
            if (!sharedId) {
                return;
            }
            var row = $(this);
            $.ajax({
                type: "GET",
                url: "/getEntry",
                data: { shared_id: sharedId },
                success: function (data) {
                    clearSelectedRow();
                    row.addClass("selected");
                    selectedRow = row;
                    showEntryViewer(data);
                }
            });
        });
    }

    $("#entry_viewer_close").on("click", function () {
        hideEntryViewer();
    });

    $(document).on("keydown", function (event) {
        if (event.key === "Escape") {
            hideEntryViewer();
        }
    });

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
                bindEntryRows();
            }
        });
    });
    // trigger submit to get the initial table of entries:
    $("#search_form").submit();
});
