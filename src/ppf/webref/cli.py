import click
from getpass import getpass
import bcrypt
import sys
from .model import db, User


@click.command('useradd')
@click.argument('username')
def useradd_command(username):
    """Register a new user."""
    # Make sure relevant tables exist:
    db.create_all()
    # Create user <username> without password:
    user = User(username=username, password=None)
    # Check whether this user already exists:
    if User.query.filter_by(username=username).first():
        print(f'User {username} already exists.')
        sys.exit(1)
    # Otherwise, add user to database:
    db.session.add(user)
    db.session.commit()
    print(f'Added user {username}')


@click.command('userdel')
@click.argument('username')
def userdel_command(username):
    """Delete user username."""
    # Make sure relevant tables exist:
    db.create_all()
    # Check whether this user already exists:
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f'User {username} does not exist.')
        sys.exit(1)
    # Otherwise, delete user from database:
    db.session.delete(user)
    db.session.commit()
    print(f'Deleted user {username}')


@click.command('passwd')
@click.argument('username')
def passwd_command(username):
    """Change password of user 'username'."""
    # Make sure relevant tables exist:
    db.create_all()
    # Check whether this user already exists:
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f'User {username} does not exist.')
        sys.exit(1)
    print(f'Changing password for {username}.')
    # If so, change password:
    password = getpass()
    # Salt it and hash it:
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    # Store it:
    user.password = bcrypt.hashpw(bytes, salt)
    db.session.commit()
    print(f'Changed password for {username}.')


def reg_cli_cmds(app):
    app.cli.add_command(useradd_command)
    app.cli.add_command(passwd_command)
    app.cli.add_command(userdel_command)
