from flask import Flask, redirect, url_for, render_template
# render_template allow us to grab an html file and render that as our webpage

# imp to name ur folder "templates" and it is in the same directory with the py file that is running the website

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/<name>/")
def user(name):
    return render_template("user.html", content=['a', 'b', 'c', 'd'], var=99)

if __name__ == "__main__":
    app.run()