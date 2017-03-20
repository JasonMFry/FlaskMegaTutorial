#  -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_TRACK_MODIFICATIONS = False

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
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = os.environ.get('MAIL_PORT', 465)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', False)
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', True)
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'fbloginjunk@gmail.com')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'GmMcY4JiRptmZoD0m02Af5Ap5ldBfG5s5iNX')

# administrator list
ADMINS = ['fbloginjunk@gmail.com']

# pagination
POSTS_PER_PAGE = 3

# text search
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50

# available languages
LANGUAGES = {
	'en': 'English',
	'es': 'Español'
}
