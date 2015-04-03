from flask import render_template, request, redirect, url_for, flash, session
from flask.ext.login import login_user, logout_user, current_user, login_required
from tzundoku import tzundoku, db
from .forms import LoginForm, RegistrationForm, AddDokuForm, AddItemForm, AddPostForm
from .models import User, Doku, Item, Post

import datetime
import legal

@tzundoku.route('/')
@tzundoku.route('/index')
def index():
    return render_template('index.html') 

@tzundoku.route("/login", methods=['GET', 'POST'])
def login(): 
    form = LoginForm() 
    if 'email' in session:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('login.html', form=form)
        else:
            user = User.query.filter_by(username = form.username.data).first()
            session['email'] = user.email 

            return redirect(url_for('overview'))
    elif request.method == 'GET':
        return render_template('login.html', title='Login', form=form)

@tzundoku.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if 'email' in session:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('register.html', form=form)
        else:
            user = User(form.username.data, form.email.data, form.password.data)
            db.session.add(user)
            db.session.commit()
            session['email'] = user.email
            flash('You have created a new account')
            return redirect(url_for('overview')) 

    elif request.method == 'GET':
        return render_template('register.html', form=form)  

@tzundoku.route("/logout")
def logout():
    if 'email' not in session:
        return redirect(url_for('login'))
    session.pop('email', None)
    return redirect(url_for('index')) 

@tzundoku.route("/overview", methods=['GET', 'POST'])
def overview():
    form = AddDokuForm()
    user = User.query.filter_by(email= session['email']).first()

    titles = []
    doku = Doku.query.all()
    for a in doku:
        if a.parent == "Top":
            titles.append(a)
            for b in doku:
                if b.parent == a.title:
                    titles.append(b)
                    for c in doku:
                        if c.parent == b.title:
                            titles.append(c)


     
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('overview.html', titles=titles, form=form)
        else:
            doku = Doku(form.title.data, form.parent.data, user.id, datetime.datetime.utcnow())
            db.session.add(doku)
            db.session.commit()
            flash('You have created a new Doku!')
            return redirect(url_for('overview')) 

    elif request.method == 'GET':
        return render_template('overview.html', titles=titles, form=form)  

@tzundoku.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(email= session['email']).first()
    
    if user is None:
        return redirect(url_for('login'))
    else:
        username = user.username
        return render_template('profile.html', username=username)

@tzundoku.route('/user/<id>')
def user(id):
    user = User.query.filter_by(id=id).first()
    if user == None:
        flash('User %s not found.' % user.username)
        return redirect(url_for('overview'))
    posts = Post.query.filter_by(added_by=id)
    return render_template('user.html',
                           user=user,
                           posts=posts)

@tzundoku.route('/testdb')
def testdb():
    if db.session.query("1").from_statement("SELECT 1").all():
        return 'It Works.'
    else:
        return 'Something is broken'

@tzundoku.route('/terms')
def terms():
    return render_template('legal.html',
                           title="Terms and Conditions",
                           content=legal.terms)
@tzundoku.route('/privacy')
def privacy():
    return render_template('legal.html',
                           title="Privacy Policy",
                           content=legal.privacy)

@tzundoku.route('/doku', methods=['GET', 'POST'])
def doku():
    user = User.query.filter_by(email= session['email']).first()
    form = AddItemForm()
    itemdokuid = request.args['id']
    doku = Doku.query.filter_by(id = itemdokuid).first()
    header = doku.title
    items = Item.query.filter_by(doku_id = itemdokuid)
    
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('doku.html', header=header, items=items, form=form)
        else:
            item = Item('music', form.title.data, form.artist.data, form.year.data, form.link.data, user.username, datetime.datetime.utcnow(), itemdokuid)
            db.session.add(item)
            db.session.commit()
            session['email'] = user.email
            flash('You have added an item')
            return redirect(url_for('doku', id=itemdokuid)) 

    elif request.method == 'GET':
        return render_template('doku.html', header=header, items=items, form=form)  


@tzundoku.route('/item/<id>', methods=['GET', 'POST'])
def item(id):
    user = User.query.filter_by(email= session['email']).first()
    form = AddPostForm()
    item = Item.query.filter_by(id = id).first()
    header = item.title
    posts = Post.query.filter_by(item_id = id)


    if request.method == 'POST':
        if form.validate() == False:
            return render_template('item.html', header=header, posts=posts, form=form)
        else:
            post = Post(user.id, form.message.data, datetime.datetime.utcnow(), id)
            db.session.add(post)
            db.session.commit()
            flash('You have added a post!')
            return redirect(url_for('item', id=id)) 

    elif request.method == 'GET':
        return render_template('item.html', header=header, posts=posts, form=form)
    

