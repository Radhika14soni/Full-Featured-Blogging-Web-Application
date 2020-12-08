from flaskblog import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin 
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


'''
Flask-login requires a User model with the following properties:

has an is_authenticated() method that returns True if the user has provided valid credentials
has an is_active() method that returns True if the user’s account is active
has an is_anonymous() method that returns True if the current user is an anonymous user
has a get_id() method which, given a User instance, returns the unique ID for that object
 is_authenticated, is_anonymous, get_active, get_id()

To make implementing a user class easier, you can inherit from UserMixin, 
which provides default implementations for all of these properties and methods. (It’s not required, though.)
'''

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

'''
@login_manager.user_loader
This sets the callback for reloading a user from the session. 
The function you set should take a user ID (a unicode) and return a user object,
 or None if the user does not exist.
'''


class User(db.Model, UserMixin):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    bio = db.Column(db.String(50), nullable=True) #new
    image_file = db.Column(db.String(20), nullable=False,default='default.jpg')
    password = db.Column(db.String(60), nullable=False) #As hashed password will be 60 char long.
    
    
    posts = db.relationship('Post',backref='author',lazy=True) #Capital P as we are referencing actual Post class.
    comments = db.relationship('Comment', backref='commenter',lazy=True)
    postlike = db.relationship('Postlike',backref='post_liked_by',lazy=True)

    def get_reset_token(self,expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_secret_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id'] #This comes from get_reset_token
        except:
            return None   #Incase user isn't matching or timeout happens
        return User.query.get(user_id)
        


    def __repr__(self):         #This is how our object will be printed.
        return f"User('{self.username}','{self.email}','{self.image_file}','{self.bio}' )"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,default = datetime.utcnow) #Here we are not using utcnow() bcoz we want to pass this as an argument.
    last_edited = db.Column(db.DateTime, nullable=True,default = datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text,nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False) #Here u as for foreign key we are ref. column and table name.

    likes = db.relationship('Postlike',backref='P_liked',lazy=True,cascade="all, delete-orphan")
    comment = db.relationship('Comment',backref='comment_on',lazy=True,cascade="all, delete-orphan")

    
    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"


class Comment(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.Text, nullable=False)
    published = db.Column(db.DateTime, nullable=False,default = datetime.utcnow)
    
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


    def __repr__(self):
        return f"Comment('{self.author_id}','{self.published}','{self.content}')"


class Postlike(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'),nullable=False)
    liker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
           return f"Postlike('{self.liker_id}','{self.post_id}')"
 

