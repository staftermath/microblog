from app import db
from flask_login import UserMixin
from hashlib import md5

followers = db.Table('followers',
        db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
        db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
    )


class User(UserMixin, db.Model):
    __tablename__ = 'users'
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
                                secondaryjoin=(followers.c.follower_id == id),
                                backref=db.backref('followers', lazy='dynamic'),
                                lazy='dynamic'
                                )

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def is_authenticated(self):
        return True

    # @property
    def is_active(self):
        return True

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
        return None
    
    def unfollow(self, user):
        if self.is_following(user):
            # print("Following " + str(user))
            self.followed.remove(user)
            return self
        return None

    def is_following(self, user):
        count = self.followed.filter(followers.c.followed_id == user.id).count()
        # print("Found " + str(count) + " followed")
        return count > 0

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)


