from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'as12de4322dgt5eft5'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))

    def __init__(self, title, body ):
        self.title = title
        self.body = body


@app.route('/blog')
def blog():

    blogs = Blog.query.all()
    return render_template('blog.html',title="Build a Blog", blogs = blogs)

@app.route('/post')
def post():
    return render_template('post.html')

@app.route('/newpost', methods = ['POST', 'GET'])
def newpost():
    title = request.form['blog_title']
    body = request.form['blog_entry']
    if title == '' or body == '':
        flash("Please complete your entry")
        return render_template('/post.html', title = title, body = body )
    if request.method == 'POST':
        title = request.form['blog_title']
        body = request.form['blog_entry']
        new_entry = Blog(title, body)
        db.session.add(new_entry)
        db.session.commit()
        blog = Blog.query.order_by('-id').first()
        return render_template('newblogentry.html', blog = blog)

@app.route('/entry')
def entry():
    id = request.args.get('id')
    blog = Blog.query.filter_by(id=id).first()
    return render_template('entry.html', blog = blog)

if __name__ == '__main__':
    app.run()