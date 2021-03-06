from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'as12de4322dgt5eft5'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner ):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog', 'index', 'entry', 'userposts']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect ('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged In")
            return render_template('/post.html', user = user)
        elif not username:
            flash('Username incorrect', 'error')
        elif not password:
            flash('Password incorrect', 'error')
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username

            # TODO - "remember" the user has logged in"
            return render_template('/blog.html', username = username)
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
        users = User.query.all()
        return render_template('index.html', users = users)

@app.route('/blog')
def blog():
    blogs = Blog.query.all()
    return render_template('blog.html',title="Build a Blog", blogs = blogs)

@app.route('/post')
def post():
        user = User.query.filter_by(username = session['username']).first()
        return render_template('post.html', user = user)

@app.route('/newpost', methods = ['POST', 'GET'])
def newpost():
    title = request.form['blog_title']
    body = request.form['blog_entry']
    owner = User.query.filter_by(username = session['username']).first()
    if title == '' or body == '':
        flash("Please complete your entry")
        return render_template('/post.html', title = title, body = body )
    if request.method == 'POST':
        title = request.form['blog_title']
        body = request.form['blog_entry']
        owner = User.query.filter_by(username = session['username']).first()
        new_entry = Blog(title, body, owner)
        db.session.add(new_entry)
        db.session.commit()
        blog = Blog.query.order_by('-id').first()
        user = User.query.filter_by(username = session['username']).first()
        return render_template('entry.html',user = user, blog = blog)

@app.route('/entry')
def entry():
    id = request.args.get('id')
    blog = Blog.query.filter_by(id=id).first()
    user = request.args.get('user')
    owner = User.query.filter_by(username=user).first()
    blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('entry.html', blog = blog)

@app.route('/userposts')
def userposts():
    user = request.args.get('user')
    owner = User.query.filter_by(username=user).first()
    blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('userposts.html', blogs = blogs)

if __name__ == '__main__':
    app.run()