# ppf.webref

ppf.webref is a web app providing an interface to a [JabRef SQL
database](https://docs.jabref.org/collaborative-work/sqldatabase).
Access your references from anywhere in the world and from any device with a
web browser. You do not need to install Java, you do not need to install an
app. Any non-archaic phone, tablet, PC, Mac, or Raspberry Pi will do.

Create a JabRef database (using your normal JabRef) and point ppf.webref to
this database. Voila: Your references just became accessible worldwide.

Note: ppf.webref provides *read-only* access to your library. To add, edit, or
delete entries from your library, you still need a standard JabRef installation
somewhere.

<p align="middle">
<img alt="Screenshot" src="imgs/webref_screenshot.png" height=180>
</p>


# Installation

Prerequisite: You need JabRef to create, edit, and extend your library.

Install `ppf.webref` (or have a look at
[docker.webref](https://github.com/adrianschlatter/docker.webref) that provides
a docker container running `ppf.webref`):

```shell
pip install ppf.webref
```

Then, tell ppf.webref about your database by adding a section as follows to
`~/.config/ppf.webref/ppf.webref.conf` (create it if it does not exist):

```
[flask]
secret_key = <your secret key here>

[database]
server = <server>:<port>
databasename = <name of your jabref database>
username = <username ppf.webref should use to access db>
password = <password ppf.webref should use to access db>
```

`secret_key` is needed to encrypt cookies. Set it to a random string, e.g. by
running this snippet:

```shell
python -c 'import secrets; print(secrets.token_hex())'
```

Finally, run

```shell
flask --app ppf.webref run
```

and point your webbrowser to http://localhost:5000.

[This will start ppf.webref on your local machine which is nice for testing.
To get the most out of ppf.webref, you will probably want to run ppf.webref on
a web server.]

ppf.webref will present a login form. However, as we have not created any users
yet, we can't login. To create a user, run:

```shell
flask --app ppf.webref useradd <username>
```

This will:

* create a table 'user' in your db if it does not exist, yet
* register user <username> in user table

To set a password for this new user or to change the password of an existing
user, do

```shell
flask --app ppf.webref passwd <username>
```

which will ask for and store (a salted hash of) the password in the
user table.

Now we are able to login, but the entry table will not provide links to our
documents. For `ppf.webref` to be able to serve the documents themselves, we
have to put them under `<app.root_path>/references` (just place a symlink to
your JabRef library there). The app's root path is something like
`/usr/local/lib/python3.11/site-packages/ppf/webref/`.


# Still reading?

If you read this far, you're probably not here for the first time. If you use
and like this project, would you consider giving it a Github Star? (The button
is at the top of this website.) If not, maybe you're interested in one of my
[my other
projects](https://github.com/adrianschlatter/ppf.sample/blob/develop/docs/list_of_projects.md)?


# Contributing

Did you find a bug and would like to report it? Or maybe you've fixed it
already or want to help fixing it? That's great! Please read
[CONTRIBUTING](./CONTRIBUTING.md) to learn how to proceed from there.

To help ascertain that contributing to this project is a pleasant experience,
we have established a [code of conduct](./CODE_OF_CONDUCT.md). You can expect
everyone to adhere to it, just make sure you do as well.


# Changelog

* 0.1.1: Fix problem with path handling. Improve README.md.
* 0.1: Basic read-only functionality
