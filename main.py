from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, abort, make_response
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import random, string, requests, httplib2, json
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Post, Ads, Family, Comment

#importing for oauth2 login
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError



#securing registration
from logic import hash_str, get_date, is_safe_url

#initializing flask app and login manager
app = Flask(__name__)
app.secret_key = 'kiasu_secret'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#Connecting engine to local MySQL database named obitsy_db
engine = create_engine('mysql://obitsy:kiasu123@localhost/obitsy_db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@login_manager.user_loader
def load_user(userid):
    user_id = int(userid)
    user = session.query(User).filter_by(id=user_id).one()
    if user:
        return user
    else:
        return None

@app.route('/logout')
@login_required
def logout():
    successmsg = "You have succesfully logged out!"
    flash(render_template('success.html', successmsg=successmsg))
    logout_user()
    return redirect(url_for('main'))

#Routes to homepage
@app.route('/')
def main():
    posts = session.query(Post).all()
    print "Current user is authenticated: %s" % current_user.is_authenticated
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
                hPass = hash_str(password)
                if user.password == hPass:
                    print "User found, password matched: %s" % user.name
                    login_user(user, remember=True)
                    print "User is logged in, current user: %s" % current_user.is_authenticated
                    next = request.args.get('next')
                    if not is_safe_url(next):
                        return abort(400)

                    if next == '/logout':
                        return redirect(url_for('main'))

                    return redirect(url_for('main'))
                else:
                    return render_template('login.html', alert=render_template('alert.html', errormsg=error))
            else:
                return render_template('login.html', alert=render_template('alert.html', errormsg=error))

    else:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
        login_session['state'] = state
        return render_template('login.html', STATE=state)

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

            #Succesfully registering user
            else:
                hPass = hash_str(password)
                todayDate = get_date()
                user = User(name=name, email=email, password=hPass, member_since=todayDate)
                session.add(user)
                session.commit()
                print "Registering user: %s" % user.name
                user_created = session.query(User).filter_by(email=email).one()
                successmsg = "Registration Successful! Welcome to Kaboong..."
                login_user(user_created, remember=True)
                print "User login is invoked!"
                flash(render_template('success.html', successmsg=successmsg))
                return redirect(url_for('main'))
        else:
            error = "Please fill in all fields!"
            return render_template('register.html', alert=render_template('alert.html',errormsg=error))
    else:
        return render_template('register.html')

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    #Exchanging for long lived token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    userinfo_url = "https://graph.facebook.com/v2.5/me"
    print result
    token = result.split("&")[0]

    url = "https://graph.facebook.com/v2.8/me?%s&fields=name,id,email,picture" % token
    h = httplib2.Http()
    result = h.request(url,'GET')[1]
    data = json.loads(result)

    user = User(name=data['name'], password=data['id'], email=data['email'], member_since=get_date())
    session.add(user)
    session.commit()

    login_user(user)
    return redirect(url_for('main'))



@app.route('/user/<int:user_id>')
def userProfile(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        if current_user.id == user.id:
            posts = session.query(Post).filter_by(user=user).all()
            return render_template('user-profile.html', user=user, posts=posts)
    else:
        return redirect(url_for('main'))

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
  app.debug = True
  app.run(host = '0.0.0.0')
