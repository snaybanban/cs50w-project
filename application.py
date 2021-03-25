import os
from helpers import login_required

from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask import session
from tempfile import mkdtemp
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not ("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up database
engine = create_engine("postgres://ajigwrxxtsfjgh:eef2bb35cd85a37e7d10b5699794a552f7dd4736560b44c88126e9f1228f8f51@ec2-54-145-102-149.compute-1.amazonaws.com:5432/d8tvv4bh4q66pr")
#engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))  

@app.route("/")
@login_required
def index():
    books = db.execute("SELECT * FROM books").fetchall()
    return render_template("index.html", books=books)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("VACIO")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("VACIO")
            return render_template("login.html")    
        

        # Remember which user has logged in
        rows=db.execute("SELECT * FROM users WHERE username=:username", {"username":request.form.get("username")})
        rows=rows.fetchone()
        print(rows)
        ####check contraseña
        if rows == None or not check_password_hash(rows[2], request.form.get("password")):
            print('error: contraseña incorrecta o usuario no registrado')
            return render_template("error.html")
       
        # Redirect user to home page
        print(rows[1])
        session["user_id"] = rows[0]
        return render_template("index.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Allow user to change her password"""

    if request.method == "POST":

        # Ensure current password is not empty
        if not request.form.get("password"):
            flash("ALGO SALIO MAL")
            return render_template("change_password.html")
        # Query database for user_id
        rows=db.execute("SELECT * FROM users WHERE id_user = :user", {"user":session["user_id"]}).fetchall()
        print(rows)
        # Ensure current password is correct
        if rows == None or not check_password_hash(rows[2], request.form.get("password")):
            flash("ALGO SALIO MAL")
            return render_template("change_password.html")

        # Ensure new password is not empty
        if not request.form.get("new_password"):
            flash("ALGO SALIO MAL")
            return render_template("change_password.html")

        # Ensure new password confirmation is not empty
        elif not request.form.get("new_password_confirmation"):
            flash("ALGO SALIO MAL")
            return render_template("change_password.html")

        # Ensure new password and confirmation match
        elif request.form.get("new_password") != request.form.get("new_password_confirmation"):
            flash("ALGO SALIO MAL")
            return render_template("change_password.html")
        else:
            # Update database
            hashs = generate_password_hash(request.form.get("new_password"))
            rows = db.execute("UPDATE users SET hashs = :hashs WHERE user_id = :user_id", user_id=session["user_id"], hashs=hashs)
            db.commit()
            session.clear()

            # Show flash
            flash("Changed!")
            return render_template("login.html")

    return render_template("change_password.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("index"))



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("username vacio")
            return render_template("register.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("password vacio")
            return render_template("register.html")

        # Ensure password and confirmation match
        elif not request.form.get("password") == request.form.get("confirmation"):
            flash("No coincide")
            return render_template("register.html")

        # hash the password and insert a new user in the database
        paswordhash = generate_password_hash(request.form.get("confirmation"))
        rows = db.execute("INSERT INTO users (username, hashs) VALUES(:username, :paswordhash)",{"username":request.form.get("username"), "paswordhash":paswordhash})

        db.commit()

        return render_template("login.html")
        
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/busqueda", methods=["GET", "POST"])
def busqueda():
    
    if request.method == "POST":

        return redirect(url_for("busqueda"))
