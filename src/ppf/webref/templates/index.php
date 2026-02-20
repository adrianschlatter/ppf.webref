<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>

<head>
    <meta charset="utf-8" />
    <title>ppf.webref: A Web Interface to JabRef</title>
    <link type="text/css" rel="stylesheet" href="style.css">

    <script src="https://code.jquery.com/jquery-3.5.1.min.js"
        integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0="
        crossorigin="anonymous"></script>
    <script
        src="https://cdnjs.cloudflare.com/ajax/libs/jquery.form/4.3.0/jquery.form.min.js"
        integrity="sha384-qlmct0AOBiA2VPZkMY3+2WqkHtIQ9lSdAsAn5RUJD/3vA5MKDgSGcdmIv4ycVxyn"
        crossorigin="anonymous"></script>
    <script type="text/javascript" src="script.js"></script>
</head>

<body>
    <div id="top_bar">
        <h1>ppf.webref: A Web Interface to JabRef</h1>
        <p><a href="{{url_for('logout')}}">Logout</a></p>
        <form id="search_form" action="{{ url_for('loadEntries') }}">
            {{ form.csrf_token }}
            {{ form.searchexpr }}
        </form>
    </div>
    <div id="entry_table_container">
        <div id="entry_table">
            <!-- entries loaded from webserver will be shown here -->
        </div>
    </div>
    <div id="entry_viewer" class="hidden">
        <div id="entry_viewer_header">
            <h2>Entry details</h2>
            <button id="entry_viewer_close" type="button">Close</button>
        </div>
        <dl id="entry_viewer_details">
            <dt>Title</dt>
            <dd id="entry_viewer_title"></dd>
            <dt>Authors</dt>
            <dd id="entry_viewer_authors"></dd>
            <dt>Date</dt>
            <dd id="entry_viewer_date"></dd>
            <dt>Type</dt>
            <dd id="entry_viewer_type"></dd>
            <dt>Citation key</dt>
            <dd id="entry_viewer_citationkey"></dd>
            <dt>Files</dt>
            <dd id="entry_viewer_files"></dd>
        </dl>
    </div>
</body>

</html>
