from flask import Blueprint, request, flash, redirect, url_for
from flask.templating import render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect Password!", category="error")
        else:
            flash("User does not exist!", category="error")


    return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/sign-up", methods=["POST", "GET"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password1 = request.form.get("password")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()
        user_name = User.query.filter_by(name=name).first()

        if user:
            flash("Email already exists!", category="error")
        elif user_name:
            flash("Username already exists!", category="error")
        elif len(email) < 4:
            flash("Invalid Email!", category="error")
        elif len(name) < 4:
            flash("Name is too short!", category="error")
        elif password1 != password2:
            flash("Password and password confirmation do not match!", category="error")
        else:
            new_user = User(email=email, name=name, password=generate_password_hash(password1, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully!", category="success")
            login_user(new_user, remember=True)
            return redirect(url_for("views.home"))

    return render_template("sign_up.html", user=current_user)