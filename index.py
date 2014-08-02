from flask import Flask, redirect, render_template, url_for, flash, request
from wtforms import Form, StringField, validators
import os
from sqlalchemy import create_engine, Column, Integer, Text, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite:///tmp/flask-blog.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
app = Flask(__name__)
app.secret_key = "secret"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    body = Column(Text)


Base.metadata.create_all(engine)


class PostForm(Form):
    title = StringField("Title", [validators.Required()])
    body = StringField("Body", [validators.Required()])


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), "error")


@app.route("/")
def index():
    return redirect(url_for("index_posts"))


@app.route("/posts", methods=["GET"])
def index_posts():
    posts = session.query(Post).order_by(Post.id)

    return render_template("index.html", posts=posts)


@app.route("/posts", methods=["POST"])
def store_post():
    form = PostForm(request.form)
    if form.validate():
        post = Post(title=form.title.data, body=form.body.data)
        session.add(post)
        session.commit()

        return redirect(url_for("index_posts"))
    else:
        flash_errors(form)

        return redirect(url_for("create_post"))


@app.route("/posts/new")
def create_post():
    return render_template("create_post.html")


@app.route("/posts/<int:post_id>")
def show_post(post_id):
    post = session.query(Post).filter(Post.id == post_id).first()

    if post:
        return render_template("show_post.html", post=post)
    else:
        return "Post not found"


if os.environ.get('DEBUG') == "yes":
    app.debug = True
    print("Running in debug mode")

if __name__ == "__main__":
    app.run()
