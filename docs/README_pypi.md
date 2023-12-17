# ppf.webref

ppf.webref is a web app providing an interface to a [JabRef SQL
database](https://docs.jabref.org/collaborative-work/sqldatabase).
It allows you to access your references from anywhere in the world and from
any device with a web browser. You do not need to install Java, you
do not need to install an app. Any non-archaic phone, tablet, PC, Mac, or
Raspberry Pi will do.

Create a JabRef database (using your normal JabRef) and configure ppf.webref 
to point to this database. Voila: Your references just became accessible
worldwide.

Note: ppf.webref provides *read-only* access to your library. To add, edit, or
delete entries from your library, you still need a standard JabRef installation
somewhere.


## Installation

Prerequisite: You need JabRef to create, edit, and extend your library.

Install ppf.webref:

```shell
pip install ppf.webref
```

Then, tell ppf.webref about your database by adding a section as follows to
`~/.config/ppf.webref/ppf.webref.conf` (create it if it does not exist):

```
[database]
server = <server>:<port>
databasename = <name of your jabref database>
username = <username ppf.webref should use to access db>
password = <password ppf.webref should use to access db>
```

Finally, run

```shell
flask --app ppf.webref run
```

and point your webbrowser to http://localhost:5000.

This will start ppf.webref on your local machine which is nice for testing.
To get the most out of ppf.webref, you will probably want to run ppf.webref on
a web server.

As we have not created any users yet, we can't login. To create
users, open your JabRef database (the one named in the config file above)
and run this sql-code (make sure you don't have a table with this name
already):

```
create table user (
	id INT auto_increment,
	username varchar(20) character set utf8 not null,
	password char(80) character set ascii not null,
	primary key (id),
	unique(username)
)
```

Now we have a user table but no users in it, yet. Let's find a password and
hash it with the following python code (of course, we replace the dummy
password with your own password beforehand):

```
import bcrypt

password = 'This is my password'

bytes = password.encode('utf-8')
salt = bcrypt.gensalt()
print(bcrypt.hashpw(bytes, salt))
```

The output looks something like this:

```
b'$2b$12$1royHRBq6o/mbDdO7LjR8eaThWYErI6HLLdn7MBfajtpRLlwWSJ8m'
```

Now add your user to the user table in you JabRef database using this sql-code
(again, replace "webref" with your username and the password hash with the
hash you generated above):

```
insert into user (username, password)
values (
	"webref",
	"$2b$12$1royHRBq6o/mbDdO7LjR8eaThWYErI6HLLdn7MBfajtpRLlwWSJ8m"
);
```

Now we are ready to go.
