#!venv/bin/python

import os
import unittest

from config import basedir
from app import app, db
from app.models import User

class TestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_avatar(self):
		u = User(nickname='john', email='john@example.com', social_id='john')
		avatar = u.avatar(128)
		expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
		assert avatar[0:len(expected)] == expected

	def test_make_unique_nickname(self):
		u = User(nickname='john', email='john@example.com', social_id='john')
		db.session.add(u)
		try:
			db.session.commit()
		except:
			db.session.rollback()
			raise
		# nickname = User.make_unique_nickname('susan')
		# assert nickname == 'susan'
		nickname = User.make_unique_nickname('john')
		assert nickname != 'john'
		u = User(nickname=nickname, email='susan@example.com', social_id='susan')
		db.session.add(u)
		try:
			db.session.commit()
		except:
			db.session.rollback()
			raise
		nickname2 = User.make_unique_nickname('john')
		assert nickname2 != 'john'
		assert nickname2 != nickname

	def test_follow(self):
		u1 = User(nickname='john', email='john@example.com', social_id='john')
		u2 = User(nickname='susan', email='susan@example.com', social_id='susan')
		db.session.add(u1)
		db.session.add(u2)
		try:
			db.session.commit()
		except:
			db.session.rollback()
			raise
		assert u1.unfollow(u2) is None
		u = u1.follow(u2)
		db.session.add(u)
		try:
			db.session.commit()
		except:
			db.session.rollback()
			raise
		assert u1.follow(u2) is None
		assert u1.is_following(u2)
		assert u1.followed.count() == 1
		assert u1.followed.first().nickname == 'susan'
		assert u2.followers.count() == 1
		assert u2.followers.first().nickname == 'john'
		u = u1.unfollow(u2)
		assert u is not None
		db.session.add(u)
		try:
			db.session.commit()
		except:
			db.session.rollback()
			raise
		assert not u1.is_following(u2)
		assert u1.followed.count() == 0
		assert u2.followed.count() == 0

if __name__ == '__main__':
    unittest.main()
