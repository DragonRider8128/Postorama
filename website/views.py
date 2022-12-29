from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Post, Comment, User
from . import db

views = Blueprint("views", __name__)

@views.route("/")
def home():
    posts = Post.query.all()
    comments = Comment.query.all()

    return render_template("home.html", user=current_user, posts=posts, comments=comments)

@views.route("/create-post", methods=["POST","GET"])
@login_required
def create_post():
    if request.method == "POST":
        post = request.form.get("post")
        title = request.form.get("title")

        if len(title) < 1:
            flash("Please enter a title.", category="error")
        elif len(post) < 1:
            flash("Please enter some content.", category="error")
        else:
            new_post = Post(data=post, author=current_user.id, title=title)
            db.session.add(new_post)
            db.session.commit()
            flash("Your post is now published!", category="success")


    return render_template("create_post.html", user=current_user)

@views.route("/my-posts")
@login_required
def my_posts():
    return render_template("my_posts.html",user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if post:
        if post.author == current_user.id:
            db.session.delete(post)
            db.session.commit()
            flash("Post deleted successfully.", category="success")
        else:
            flash("Permission Denied!", category="error")
    else:
        flash("Post does not exist!", category="error")

    return redirect(url_for("views.my_posts"))

@views.route("/delete-comment/<id>")
@login_required
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()

    if comment:
        post = Post.query.filter_by(id=comment.post).first()
        if comment.user == current_user.id or post.author == current_user.id:
            db.session.delete(comment)
            db.session.commit()
            flash("Comment deleted successfully.", category="success")
        else:
            flash("Permission Denied!", category="error")
    else:
        flash("Comment does not exist!", category="error")
    
    return redirect(url_for("views.home"))

@views.route("/comment/<id>", methods=["POST","GET"])
@login_required
def comment(id):
    if request.method == "POST":
        post = Post.query.filter_by(id=id).first()

        if post:
            comment = request.form.get("comment-text")

            if len(comment) < 1:
                flash("Please enter a comment.", category="error")
            else:
                new_comment = Comment(text=comment, user=current_user.id, post=post.id)
                db.session.add(new_comment)
                db.session.commit()
        else:
            flash("Post does not exist!", category="error")
    
    return redirect(url_for("views.home"))

@views.route("/users/<name>")
def posts(name):
    user = User.query.filter_by(name=name).first()
    if user:
        posts = user.posts
        return render_template("posts.html", posts=posts, name=name, user=current_user, post_creator=user)
    else:
        flash("User does not exist!", category="error")
        return redirect(url_for("views.home"))

@views.route("/account", methods=["POST", "GET"])
@login_required
def account():
    return render_template("account.html", user=current_user)

@views.route("/update-account", methods=["POST","GET"])
@login_required
def update_account():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")

        user = User.query.filter_by(email=email).first()
        user_name = User.query.filter_by(name=name).first()

        if user and not user.email == current_user.email:
            flash("Email already exists!", category="error")
        elif user_name and not user_name.name == current_user.name:
            flash("Username already exists!", category="error")
        else:
            current_user.name = name
            current_user.email = email
            db.session.commit()
            flash("Account updated successfully!", category="success")
    
    return redirect(url_for("views.account"))

@views.route("/change-password", methods=["POST", "GET"])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get("password1")
        new_password = request.form.get("password2")

        if check_password_hash(current_user.password, old_password):
            if len(new_password) >= 8:
                current_user.password = generate_password_hash(new_password, method="sha256")
                db.session.commit()
                flash("Password Changed!", category="success")
            else:
                flash("Password must be greater than 8 characters.", category="error")
        else:
            flash("Current password is incorrect!", category="error")
        
    return redirect(url_for("views.account"))


@views.route("/delete-account", methods=["POST", "GET"]) 
@login_required
def delete_account():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")

        if email != current_user.email:
            flash("Incorrect email!", category="error")
        elif name != current_user.name:
            flash("Incorrect username!", category="error")
        elif not check_password_hash(current_user.password, password):
            flash("Incorrect password!", category="error")
        else:
            user_posts = Post.query.filter_by(author=current_user.id).all()
            user_comments = Comment.query.filter_by(user=current_user.id).all()
            

            for i in range(len(user_posts)):
                db.session.delete(user_posts[i])

            for i in range(len(user_comments)):
                db.session.delete(user_comments[i])

            db.session.delete(current_user)
            db.session.commit()
            
            flash("Account deleted successfully!", category="success")
            return redirect(url_for("auth.login"))
    
    return redirect(url_for("views.account"))

            