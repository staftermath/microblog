from app import db
from flask_login import UserMixin
from hashlib import md5

followers = db.Table('followers',
        db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
    )


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    followed = db.relationship('User',
                                secondary=followers,
                                primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.followed_id == id),
                                backref=db.backref('followers', lazy='dynamic'),
                                lazy='dynamic'
                                )

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    # @property
    def is_authenticated(self):
        return True

    # @property
    def is_active(self):
        return True

    # @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' \
        % (md5(self.email.encode('utf-8')).hexdigest(), size)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def follow(self, user):
        if not self.is_following(user):
            # print("Not following " + str(user))
            self.followed.append(user)
            return self
    
    def unfollow(self, user):
        if self.is_following(user):
            # print("Following " + str(user))
            self.followed.remove(user)
            return self

    def is_following(self, user):
        count = self.followed.filter(followers.c.followed_id == user.id).count()
        # print("Found " + str(count) + " followed")
        return count > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == \
                    Post.user_id)).filter(followers.c.follower_id == \
                    self.id).order_by(Post.timestamp.desc())

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)

class Deal(db.Model):
    __tablename__ = 'deals'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(32), index=True)
    dealName = db.Column(db.String(140), index=True)
    startTime = db.Column(db.DateTime)
    endTime = db.Column(db.DateTime)
    url = db.Column(db.String(300))
    price = db.Column(db.Float)
    expired = db.Column(db.Boolean)

    def __repr__(self):
        return '%r: %r' % (self.category, self.dealName)

