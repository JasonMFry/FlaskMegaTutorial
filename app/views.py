from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .models import User, Post
from oauth import OAuthSignIn
from datetime import datetime
from .forms import LoginForm, EditForm, PostForm, SearchForm
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, LANGUAGES
from .emails import follower_notification
from app import babel
from flask_babel import gettext


@babel.localeselector
def get_locale():
	return request.accept_languages.best_match(LANGUAGES.keys())

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))


@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated:
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()
		g.search_form = SearchForm()
	g.locale = get_locale()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
		db.session.add(post)
		db.session.commit()
		flash(gettext('Your post is now live!'))
		return redirect(url_for('index'))
	posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
	return render_template('index.html',
						   title='Home',
						   form=form,
						   posts=posts)


@app.route('/login')
def login():
	return render_template('login.html', title='Sign In')

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
	if not current_user.is_anonymous: #tutorial has is_anonymous(), but throws bool error.
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
	if not current_user.is_anonymous: #tutorial has is_anonymous(), but throws bool error.
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	social_id, username, email = oauth.callback()
	if social_id is None:
		flash(gettext('Authentication failed.'))
		return redirect(url_for('index'))
	user = User.query.filter_by(social_id=social_id).first()
	if not user:
		nickname = User.make_valid_nickname(nickname)
		nickname = User.make_unique_nickname(nickname)
		user = User(social_id=social_id, nickname=nickname, email=email)
		db.session.add(user)
		db.session.commit()
		# make the user follow him/herself
		db.session.add(user.follow(user))
		db.session.commit()
	login_user(user, True)
	return redirect(url_for('index'))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
	user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash(gettext('User %s not found.' % nickname))
		return redirect(url_for('index'))
	posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
	return render_template('user.html', user=user, posts=posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user.nickname)
	if form.validate_on_submit():
		g.user.nickname = form.nickname.data
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash(gettext('Your changes have been saved.'))
		return redirect(url_for('edit'))
	else:
		form.nickname.data = g.user.nickname
		form.about_me.data = g.user.about_me
	return render_template('edit.html', form=form)

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
	user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash(gettext('User %s not found.' % nickname))
		return redirect(url_for('index'))
	if user == g.user:
		flash(gettext('You can\'t follow yourself!'))
		return redirect(url_for('user', nickname=nickname))
	u = g.user.follow(user)
	if u is None:
		flash(gettext('Cannot follow'), nickname + '.')
		return redirect(url_for('user', nickname=nickname))
	db.session.add(u)
	db.session.commit()
	flash(gettext('You are now following'), nickname + '!')
	follower_notification(user, g.user)
	return redirect(url_for('user', nickname=nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
	user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash(gettext('User %s not found.' % nickname))
		return redirect(url_for('index'))
	if user == g.user:
		flash(gettext('You can\'t unfollow yourself!'))
		return redirect(url_for('user', nickname=nickname))
	u = g.user.unfollow(user)
	if u is None:
		flash(gettext('Cannot unfollow'), nickname + '.')
		return redirect(url_for('user', nickname=nickname))
	db.session.add(u)
	db.session.commit()
	flash(gettext('You have stopped following'), nickname + '.')
	return redirect(url_for('user', nickname=nickname))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
	post = Post.query.get(id)
	if post is None:
		flas(gettext('Post not found.'))
		return redirect(url_for('index'))
	if post.author.id != g.user.id:
		flash(gettext('You cannot delete this post.'))
		return redirect(url_for('index'))
	db.session.delete(post)
	db.session.commit()
	flash(gettext('Your post has been deleted.'))
	return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
@login_required
def search():
	if not g.search_form.validate_on_submit():
		return redirect(url_for('index'))
	return redirect(url_for(
							'search_results',
							query=g.search_form.search.data)
	)

@app.route('/search_results/<query>')
@login_required
def search_results(query):
	results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
	return render_template('search_results.html',
							query=query,
							results=results)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template('500.html'), 500