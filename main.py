from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def incricao():
    if request.method == "POST":
        name = request.form["nomeForm"]
        church = request.form["churchForm"]
        celphone = request.form["celForm"]
        email = request.form["emailForm"]
        remedy = request.form["remedyForm"]
        hour_remedy = request.form["hourForm"]

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)