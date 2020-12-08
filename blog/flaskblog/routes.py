import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import RegistrationForm, LoginForm, EditProfileForm, PostForm, SearchForm, CommentForm, RequestResetForm,ResetPasswordForm
from flaskblog.models import User, Post, Comment, Postlike
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message



@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5) #By using order by desc we'll get the newest post first
    categories = Post.query.with_entities(Post.category).distinct().all()
    return render_template('home.html', posts=posts,categories=categories)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:  # This will send us back to home page when we try to register or login when already  logged in.
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #As we want it in string instead of byte, we use decode() 
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # This will send us back to home page when we try to register or login when already  logged in.
        return redirect(url_for('home'))

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # As we are logging in by EMAIL
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')            #flask.Request.args A MultiDict with the parsed contents of the query string.
            return redirect(next_page) if next_page else redirect(url_for('home')) #(The part in the URL after the question mark).
            
            flash('Logged In Successfully.','success')
           
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

"""
@app.route("/fornerds")
@login_required
def fornerds():
    return render_template("fornerds.html",title="For Nerds")
"""


@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    image_file = url_for('static',filename = 'profile_pic/' + current_user.image_file)
    user = User.query.filter_by(username=current_user.username).first()
    posts = user.posts
    return render_template('account.html', title='Account',image_file=image_file,posts=posts)
     

#This function will return a random 8 digit text which will be the name of the new profile picture(Same as we did in encrypting password)
def save_picture(form_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_pic.filename)
    pic_filename = random_hex + f_ext
    pic_path = os.path.join(app.root_path,'static\profile_pic',pic_filename)


    output_size = (125,125)
    i = Image.open(form_pic)
    i.thumbnail(output_size)


    i.save(pic_path) #picture saved in filesystem

    return pic_filename


@app.route('/search',methods=['GET','POST'])
def search():
    form = SearchForm()
    cat = Post.query
    categories = Post.query.with_entities(Post.category).distinct().all()


    if form.validate_on_submit():
        cat = cat.filter(Post.category.like('%'+form.category.data+'%')).all()

    return render_template('postlist.html', form=form,categories = categories,cat = cat)




@app.route("/account/editaccount", methods=['GET','POST'])
@login_required
def editaccount():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.pic.data:
            old_pic = current_user.image_file
            picture_file = save_picture(form.pic.data)
            current_user.image_file = picture_file
            if old_pic != 'default.jpg':
                os.remove(os.path.join(app.root_path, 'static/profile_pic', old_pic))
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Changes Saved!!', 'success')
        return redirect(url_for('account'))
    elif request.method=='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio 
        image_file = url_for('static',filename = 'profile_pic/' + current_user.image_file)


    return render_template('editaccount.html', title='Edit Account',image_file=image_file,form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('Logged Out Successfully.','success')
    return redirect(url_for('home'))


@app.route("/post/new", methods=['GET','POST'])
@login_required
def newpost():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content=form.content.data,category=form.category.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post Created!!', 'success')
        return redirect(url_for('home'))
    return render_template('createpost.html',title='New Post',form=form,legend='New Post')


@app.route("/post/<int:post_id>",methods=['GET','POST'])  #<> is nothing but variable which can be of any datatype
def post(post_id):
    post = Post.query.get_or_404(post_id) #get_or_404 will return the post with respective ID if it exists or will give 404 error.
    likes = Postlike.query.filter_by(post_id=post_id).count()
    action='Like'
    cs = Comment.query.filter_by(content_id=post_id)


    like = Postlike()
    user = Postlike.query.filter_by(liker_id=current_user.id,post_id=post_id).first()
    if(user):
        action = 'Unlike'
      
        
    form = CommentForm()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            comment = Comment(content=form.content.data,commenter=current_user,comment_on=post)
            db.session.add(comment)
            db.session.commit()
            flash('Comment Added!!', 'success')
            return redirect(url_for('post',post_id=post_id))
    elif request.method=='POST':
        flash('Register/Login required to comment','danger')
        return redirect(url_for('post',post_id=post_id))
        
    
    return render_template('post.html',title=post.title,form=form, post=post,cs=cs,likes=likes,action=action)


@app.route("/post/<int:post_id>/update",methods=['GET','POST']  ) 
@login_required
def updatepost(post_id):
    post = Post.query.get_or_404(post_id) 
    if post.author!=current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = form.category.data
        post.content = form.content.data
        db.session.commit() #Not using add here as we're just changing some data which already exists
        flash('Updated Successfully!!','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method=='GET':
        form.title.data = post.title
        form.category.data = post.category
        form.content.data = post.content
    return render_template('createpost.html',title='Update Post',form=form,legend='Update Post')


@app.route("/post/<int:post_id>/delete",methods=['POST']  ) 
@login_required
def deletepost(post_id):
    post = Post.query.get_or_404(post_id) 
    #like = Postlike.query.get(post_id=post_id)
    #categories = Post.query.with_entities(Post.category).distinct().all()

    #comment = Comment.query.filter_by(content_id=post_id).all()
    if post.author!=current_user:
        abort(403)
        
    #db.session.delete(like)
    db.session.delete(post)
    
    db.session.commit()
    flash('Post'+' '+post.title+' '+'Deleted Successfully!','success')
    return redirect(url_for('home'))

@app.route("/post/<int:post_id>/like",methods=['POST','GET']  ) 
@login_required
def likepost(post_id):
    action='like'
    like = Postlike()
    user = Postlike.query.filter_by(liker_id=current_user.id,post_id=post_id).first()
    if(user):
        action = 'Unlike'
        db.session.delete(user)
        db.session.commit()     
        return redirect(url_for('post',post_id=post_id))
    
    like.post_id=post_id
    like.liker_id=current_user.id
    db.session.add(like)
    db.session.commit()
    return redirect(url_for('post',post_id=post_id,action=action))



@app.route("/user/<string:username>")
@login_required
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_secret_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
