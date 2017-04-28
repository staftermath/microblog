import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '1312261178864314',
        'secret': 'f117eb57dffc980f5cdb4734e3efc5a4'
    },
    'twitter': {
        'id': '3RzWQclolxWZIMq5LJqzRZPTl',
        'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
    }
}
OPENID_PROVIDERS = [
	{'name': 'Google', 'url':"https://www.google.com/accounts/o8/id"},
	{'name': 'Yahoo', 'url':"https://me.yahoo.com"},
]

# mail server settings
MAIL_SERVER = '127.0.0.1'
MAIL_PORT = 25
MAIL_USERNAME = "gwengww"
MAIL_PASSWORD = None

# administrator list
ADMINS = ['admin@microblog.com']