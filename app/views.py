from datetime import datetime
from flask import render_template, flash, redirect, session, url_for, request, g, abort
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm, EditForm, PostForm
from .models import User, Post
from .oauth import OAuthSignIn
from config import POSTS_PER_PAGE
# ANONYMOUS = ANONYMOUS_USER()
# lm.anonymous_user = ANONYMOUS_USER()
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
		test = User.query.filter_by(nickname=g.user.nickname).count()
		print(test)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
	user = g.user
	print("I am following " + str(user.is_following(user)))
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data, timestamp=datetime.utcnow(),
					author=user)
		db.session.add(post)
		db.session.commit()
		flash('Your post is now live!')
		return redirect(url_for('index'))
	posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
	return render_template('index.html',
							title="Home",
							user=user,
							form=form,
							posts=posts)

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user)

        flash('Logged in successfully.')

        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        if not is_safe_url(next):
            return abort(400)

        return redirect(next or url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	social_id, username, email = oauth.callback()
	if social_id is None:
		flash('Authentication failed.')
		return redirect(url_for('index'))
	user = User.query.filter_by(social_id=social_id).first()
	if not user:
		user = User(social_id=social_id, nickname=username, email=email)
		db.session.add(user)
		db.session.commit()
	u = user.is_following(user)
	if u is False:
		print("Trying to follow oneself")
		db.session.add(user.follow(user))
		db.session.commit()
	login_user(user)
	return redirect(url_for('index'))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
	user = User.query.filter_by(nickname=nickname).first()
	if user == None:
		flash('User %s not found.' % nickname)
		return redirect(url_for('index'))
	posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
	return render_template('user.html',
							user=user,
							posts=posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user.nickname)
	if form.validate_on_submit():
		g.user.nickname = form.nickname.data
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit'))
	else:
		form.nickname.data = g.user.nickname
		form.about_me.data = g.user.about_me
	return render_template('edit.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
	return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template("500.html"), 500

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
	user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash('User %s not found.' % nickname)
		return redirect(url_for('index'))
	if user == g.user:
		flash('You can\'t follow yourself')
		return redirect(url_for('user', nickname=nickname))
	u = g.user.follow(user)
	if u is None:
		flash('Cannot follow ' + nickname + '.')
		return redirect(url_for('user', nickname=nickname))
	db.session.add(u)
	db.session.commit()
	flash('You are now following ' + nickname + '.')
	return redirect(url_for('user', nickname=nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
	user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash('User %s not found.' % nickname)
		return redirect(url_for('index'))
	if user == g.user:
		flash('You can\'t unfollow yourself!')
		return redirect(url_for('user', nickname=nickname))
	u = g.user.unfollow(user)
	if u is None:
		flash('Cannot unfollow ' + nickname + '.')
		return redirect(url_for('user', nickname=nickname))
	db.session.add(u)
	db.session.commit()
	flash('You have stopped following ' + nickname + '.')
	return redirect(url_for('user', nickname=nickname))


