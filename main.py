from flask import Flask, request, render_template, redirect, url_for, send_file
from db import db
from models import Enrollment
from services import Service

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"

db.init_app(app)



service = Service()

@app.route("/", methods=["GET", "POST"])
def enrollment():
    if request.method == "POST":
        archive = request.files.get("proofForm")
        cpf = request.form.get("cpfForm")
        
        upload_path = service.make_dir(cpf, archive.filename)

        archive.save(upload_path)

        new_enrollment = Enrollment(
            name=request.form.get("nomeForm"),
            cpf=cpf,
            church=request.form.get("churchForm"),
            celphone=request.form.get("celForm"),
            emergency_contact=request.form.get("emergencyContactForm"),
            email=request.form.get("emailForm"),
            remedy=request.form.get("remedyForm"),
            hour_remedy=request.form.get("hourForm"),
            local_proof=upload_path,
            payment_status="PENDENTE"
        )

        service.create_enrollment(new_enrollment)

    return render_template("index.html")

@app.route("/enrollments", methods=["GET"])
def get_enrollments():
    enrollments = service.get_all_enrollments()

    return render_template("enrollments.html", enrollments=enrollments)

@app.route("/update/<int:id>", methods=["GET", "POST"])
def update_enrollments(id):
    enrollment = db.session.query(Enrollment).filter_by(id=id).first()

    if request.method == "GET":
        return render_template("enrollment_edit.html", enrollment=enrollment)
    
    if request.method == "POST":
        new_enrollment = Enrollment(
            id=enrollment.id,
            name=request.form.get("nomeForm"),
            cpf=request.form.get("cpfForm"),
            church=request.form.get("churchForm"),
            celphone=request.form.get("celForm"),
            emergency_contact=request.form.get("emergencyContactForm"),
            email=request.form.get("emailForm"),
            remedy=request.form.get("remedyForm"),
            hour_remedy=request.form.get("hourForm"),
            local_proof=enrollment.local_proof,
            payment_status=request.form.get("paymentForm")
        )

        update = service.update_enrollment(enrollment, new_enrollment)

        if update:
            return redirect(url_for("get_enrollments"))

@app.route("/export-to-excel")
def export_enrollments():
    output = service.export_to_excel()

    return send_file(output, as_attachment=True, download_name="incricoes.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
