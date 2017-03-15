import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

OAUTH_CREDENTIALS = { #tutorial has app.config['OAUTH_CRED...']' but that's unnecessary
    'facebook': {
        'id': '1837196166539923',
        'secret': 'b686b5a304e204587536042acc1fc566'
     },
    'twitter': {
        'id': '5AX8vQD41aF7btSPLJkIiuJKd',
        'secret': 'aQNQRQsPfRD3Fpz0pSgwiwyftlOZWp22b5alipQzeCakxXLM3t'
    }
}

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 2525
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['jmphry@gmail.com']