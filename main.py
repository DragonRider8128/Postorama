from website import create_app
from flask import render_template
from flask_login import current_user

app = create_app()

@app.errorhandler(404)
def error404(error):
    return render_template("404error.html", user=current_user)


if __name__ == "__main__":
    app.run(debug=True)