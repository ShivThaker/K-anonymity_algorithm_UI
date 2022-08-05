from flask import Flask, redirect, url_for

# instance of a flask web application
app = Flask(__name__)

adminOrNot = False

# now define how to access this specific page
# define the path that we will use to get to this function as flask doesn't know where it should be going to get to this page
@app.route("/") # a decorator
def homePage():
    # return some inline html
    return "This is from the homePage() function<br/><h1>hello!</h1>"

@app.route("/<name>")
def user(name):
    return f"<h1>HELLO {name}</h1>"

@app.route("/admin/")
def admin():
    if not adminOrNot:
        # return redirect(url_for("homePage"))
        return redirect(url_for("user", name="shiv!!"))
    else:
        pass

# to run this app
if __name__ == "__main__":
    app.run(debug=True)

# now definte the pages that will be on the website
# define a function which will return what will be displayed on the page

