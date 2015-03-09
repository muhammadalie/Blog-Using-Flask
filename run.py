#!flask/bin/python
import sqlite3
from flask import Flask
from flask import render_template,flash, redirect
from flask.ext.login import LoginManager
app= Flask(__name__)
app.config.from_object('config')

from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required,user_logged_in

from flask.ext.wtf import Form
from wtforms import StringField, BooleanField,PasswordField, validators,TextField,TextAreaField,IntegerField
from wtforms.validators import DataRequired
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Message, Mail
from werkzeug import generate_password_hash,check_password_hash
from datetime import datetime
try:
	c=sqlite3.connect('test.db')
	c.execute('CREATE TABLE userd(username TEXT,password TEXT)');
	c.execute('CREATE TABLE RECORD(NAME TEXT)')
	c.close()
except:
	None

class SigninForm(Form):
	username = StringField('username', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])	
class PostForm(Form):
	head = StringField('username', validators=[DataRequired()])
	address = TextAreaField(u'Mailing Address', [validators.optional(), validators.length(max=200)])
class SearchForm(Form):
	signin= StringField('signin', validators=[DataRequired()])
class CommentForm(Form):
	comment= StringField('signin', validators=[DataRequired()])
	postid=IntegerField('postid',validators=[DataRequired()])
lm=LoginManager()
lm.init_app(app)
lm.login_view = '/'
lm.login_message = u'Log in here!'
	

@lm.user_loader
def load_user(id):
	c=sqlite3.connect('test.db')
	c=c.execute('SELECT * from userd where id=(?)',[id])
	userrow=c.fetchone()
	if userrow!=None:
		return User(userrow[1],userrow[2],userrow[3],userrow[4])


@app.route('/', methods=['GET', 'POST'])
def login():
	try:
        	c=sqlite3.connect('test.db')
        	c.execute('CREATE TABLE RECORD(ID INTEGER PRIMARY KEY,HEAD TEXT,NAME BLOB,DATE TEXT)');

        	c.close()
	except:
        	None
	try:
                c=sqlite3.connect('test.db')
                c.execute('CREATE TABLE COMMENT(ID INT,COM TEXT,DATE TEXT)');

                c.close()
        except:
                None

	a="";
	sign= SigninForm()
	s=SearchForm()
	com=CommentForm()
	u=sign.username.data
	p = sqlite3.connect('test.db')
	if com.validate_on_submit():
		text=com.comment.data
		postid=com.postid.data
		p.execute("INSERT INTO COMMENT(ID,COM,DATE) VALUES(?,?,?)",[postid,text,datetime.utcnow()]);
		p.commit()
	if sign.validate_on_submit():
		passcheck=False
		user=sign.username.data
		password=sign.password.data
		m = sqlite3.connect('test.db')
		m.execute("DROP TABLE IF EXISTS LOG");
		search=m.execute("SELECT * FROM userd WHERE username = ? ",[user]);
		for i in search:
			passcheck=check_password_hash(i[1],password)
			username=i[0]
			password=i[1]
			
		if passcheck==False:
			flash("Incorrect Password or Username")
		else:
                	m.commit()
                	m.close()
	
			return redirect('/signin')
	
		
	k=p.execute('select * from RECORD')
	c=p.execute('select * from COMMENT')
	posts=[]
	comments=[]
	for x in k:
		posts.append([x[0],x[1],x[2],x[3]])
	for x in c:
		comments.append([x[0],x[1],x[2]])
	posts.sort(key=lambda x:x[2],reverse=True)

        return render_template('index.html',
			sign=sign,s=s,posts=posts,com=com,comments=comments)



@app.route('/signup',methods=['GET', 'POST'])
def signup():
	u=SigninForm()

	if u.validate_on_submit():
                user=u.username.data
		passw=generate_password_hash(u.password.data)
                c = sqlite3.connect('test.db')
		try:
			c.execute('''CREATE TABLE RECORD
                         (NAME           TEXT    NOT NULL)''');
		except:
			None
		c.execute("INSERT INTO userd(username,password) VALUES(?,?)",[user,passw]);
		c.commit()
		c.close()
		return redirect('/signup')

	return render_template('signup.html',u=u)

@app.route('/signin', methods=['GET', 'POST'])
def index():
  try:                      	

       form=PostForm()

       if form.validate_on_submit():
		head=form.head.data
               	name=form.address.data
               	conn = sqlite3.connect('test.db')
               	conn.execute("INSERT INTO RECORD (HEAD,NAME,DATE) VALUES (?,?,?)",[head,name,datetime.utcnow()]);
               	conn.commit()
               	conn.close()
               	return redirect('/signin')
       return render_template('home.html',form=form)	
			
  except:
	return render_template('/error.html')
	return redirect('/')

@app.route('/show')
def show():
   

     return render_template('show.html')

@app.route("/logout")
def logout():
	logout_user()
	c = sqlite3.connect('test.db')
	c.execute("DROP TABLE IF EXISTS LOG");
	c.commit()
	c.close()
	return redirect('/')

app.run(debug=True)

