$(document).ready(function () {
    var entryViewer = $("#entry_viewer");
    var entryViewerTitle = $("#entry_viewer_title");
    var entryViewerAuthors = $("#entry_viewer_authors");
    var entryViewerDate = $("#entry_viewer_date");
    var entryViewerType = $("#entry_viewer_type");
    var entryViewerCitationKey = $("#entry_viewer_citationkey");
    var entryViewerFiles = $("#entry_viewer_files");
    var selectedRow = null;
    var sortBy = "title";
    var sortDir = "asc";

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

    function bindSortHeaders() {
        $(".sortable").off("click").on("click", function () {
            var newSort = $(this).data("sort");
            if (!newSort) {
                return;
            }
            if (sortBy === newSort) {
                sortDir = sortDir === "asc" ? "desc" : "asc";
            } else {
                sortBy = newSort;
                sortDir = "asc";
            }
            $("#search_form").submit();
        });
    }

    function buildSortableHeader(key, label) {
        var indicator = "";
        if (sortBy === key) {
            indicator = sortDir === "asc" ? " ▲" : " ▼";
        }
        return "<th class=\"sortable\" data-sort=\"" + key + "\">" +
            label + "<span class=\"sort-indicator\">" + indicator + "</span></th>";
    }

    function buildTable(entries) {
        var html = "<table><tr>" +
            buildSortableHeader("author", "author/editor") +
            buildSortableHeader("title", "title") +
            buildSortableHeader("year", "year") +
            "</tr>";
        entries.forEach(function (entry) {
            var author = entry.author || "";
            var title = entry.title || "";
            var year = entry.year || "";
            var titleCell;
            if (entry.file) {
                titleCell = "<a href=\"" + entry.file + "\">" + title + "</a>";
            } else {
                titleCell = title;
            }
            html += "<tr class=\"entry-row\" data-shared-id=\"" + entry.shared_id + "\">" +
                "<td>" + author + "</td>" +
                "<td>" + titleCell + "</td>" +
                "<td>" + year + "</td>" +
                "</tr>";
        });
        html += "</table>";
        return html;
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
            data: form.serialize() + "&sort_by=" + encodeURIComponent(sortBy) + "&sort_dir=" + encodeURIComponent(sortDir),
            headers: { 'X-CSRFToken': form.attr('csrf_token') },
            success: function (data) {
                var entries = data.entries || [];
                var totalCount = data.total_count || 0;
                var returnedCount = data.returned_count || 0;
                var countsLabel = returnedCount + " / " + totalCount;
                var countsElement = $("#entry_counts");
                countsElement.text(countsLabel);
                countsElement.removeClass("entry-counts-limited entry-counts-ok");
                if (returnedCount < totalCount) {
                    countsElement.addClass("entry-counts-limited");
                } else {
                    countsElement.addClass("entry-counts-ok");
                }

                var html = buildTable(entries);
                document.getElementById("entry_table").innerHTML = html;
                bindEntryRows();
                bindSortHeaders();
                hideEntryViewer();
            }
        });
    });
    // trigger submit to get the initial table of entries:
    $("#search_form").submit();
});
