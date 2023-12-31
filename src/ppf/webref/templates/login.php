<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
</head>
<body>
    <h1>Login Page</h1>

    <form method="POST" action="{{ url_for('login') }}">
        {{ form.csrf_token }}
        {{ form.username }}
        {{ form.password }}
        {{ form.submit }}
        {% if form.errors %}
        {{ form.errors }}
        {% endif %}
    </form>
</body>
</html>
