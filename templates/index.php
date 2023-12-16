<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>

<head>
    <meta charset="utf-8" />
    <title>WebRef: A Web Interface to JabRef</title>
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
    <h1>WebRef: A Web Interface to JabRef</h1>
    <p style="text-align: right"><a href="{{url_for('logout')}}">Logout</a></p>
    <form id="search_form" action="loadEntries.php">
        Search: <input type="text" name="searchexpr">
    </form>
    <div id="entry_table">
        <!-- entries loaded from webserver will be shown here -->
    </div>
</body>

</html>
