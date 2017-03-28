from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)
from flask import session as login_session
import random, string
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Post, Ads, Family, Comment

#Connecting engine to local MySQL database named obitsy_db
engine = create_engine('mysql://obitsy:kiasu123@localhost/obitsy_db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#Routes to homepage
@app.route('/')
@app.route('/allposts')
def main():
    posts = session.query(Post).all()
    return render_template('home.html', posts=posts)

#Route to About us page
@app.route('/about-us')
def aboutUs():
    return render_template('about-us.html')

#Route to Contact Us page
@app.route('/contact')
def contactUs():
    return render_template('contact-us.html')

#Routes to login user
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email and password:
            error = "Invalid email/password!"
            user = session.query(User).filter_by(email=email).first()
            if user:
                if user.password == password:
                    return redirect('/')
                else:
                    return render_template('login.html', alert=render_template('alert.html', errormsg=error))
            else:
                return render_template('login.html', alert=render_template('alert.html', errormsg=error))

    else:
        return render_template('login.html')

#Routes to register a new user
@app.route('/register', methods=['GET', 'POST'])
def createUser():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirmpswd = request.form['confirmpswd']
        error = ""

        if name and email and password and confirmpswd:
            if confirmpswd != password:
                error = "Verify Password is not the same as Password!"
                return render_template('register.html', name=name, email=email, alert=render_template('alert.html', errormsg=error))

            checkUser = session.query(User).filter_by(email=email).first()

            if checkUser:
                error = "Email has been used, please use other email"
                return render_template('register.html', alert=render_template('alert.html', errormsg=error))
            else:
                user = User(name=name, email=email, password=password)
                session.add(user)
                session.commit()
                successmsg = "Registration Successful! Welcome to Dukahub..."
                flash(render_template('success.html', successmsg=successmsg))
                return redirect('/')
        else:
            error = "Please fill in all fields!"
            return render_template('register.html', alert=render_template('alert.html',errormsg=error))
    else:
        return render_template('register.html')

@app.route('/user/<int:user_id>')
def userProfile(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        posts = session.query(Post).filter_by(user=user).all()
        return render_template('user-profile.html', user=user, posts=posts)
    else:
        return redirect('/')

@app.route('/user/<int:user_id>/edit')
def editUserProfile(user_id):
    return "Edit page for user %s" % user_id

#Routes to create new post, check, edit & delete a single post
@app.route('/newpost')
def createNewPost():
    return "Page to create new post"

@app.route('/post/<int:post_id>')
def getSinglePost(post_id):
    return "Single Post Page"

@app.route('/post/<int:post_id>/edit')
def editPost(post_id):
    return "Page to edit Single Post"

@app.route('/post/<int:post_id>/delete')
def deletePost(post_id):
    return "Page to delete post %s" % post_id

#Routes to create ads for any post
@app.route('/post/<int:post_id>/createAds')
def createAds(post_id, user_id):
    return "Create Ads for posts"

if __name__ == '__main__':
  app.secret_key = 'kiasu_secret'
  app.debug = True
  app.run(host = '0.0.0.0')
