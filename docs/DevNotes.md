# Development Notes


## Flask

* Project  layout follows [Flask's
  Tutorial](https://flask.palletsprojects.com/en/3.0.x/tutorial/layout/) but
  uses a namespace package-layout
* AJAX: ppf.webref main page sends a document and javascript. When doing
  things, events are trigged that
      - request new data from the backend
      - modify the document based on new data


## Security

* CSP (Content Security Policy):
    - based on flask_talisman
    - Follow hints by [Mozilla Observatory](https://observatory.mozilla.org)
      and make sure we get an A+
* CSRF (Cross-Site Request Forgery):
    - based on flask_wtf
    - read
      [CSRF Protection](https://flask-wtf.readthedocs.io/en/0.15.x/csrf/#javascript-requests)
    - If you run into the "Bad Request - The CSRF session token is missing."
      problem, make sure to read [Fix Missing CSRF Token Issues with
      Flask](https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask)
    - And if you start losing your mind while trying to fix CSRF problems: Try
      running it in your production environment. I was unable to make it work
      locally, I was unable to make it work on a test host, but it works on my
      production server. Maybe this is related to the cookie problem related to
      FQDNs mentioned in the article above: Neither my local computer nor my
      test host have a fully qualified domain name but my production server
      has.
* login: JabRef library is only available to logged-in users


## Tests

* pytest
* read [Testing Flask
  Applications](https://flask.palletsprojects.com/en/2.2.x/testing/)
