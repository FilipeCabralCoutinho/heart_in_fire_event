from flask import render_template, request, Blueprint, redirect, url_for, send_file, session, current_app
from services import Service
from models import Enrollment
from services import Service
import os
from auth import login_required
from db import db

routes = Blueprint("routes", __name__)

service = Service()

@routes.route("/", methods=["GET", "POST"])
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

        enrollment_dict = service.obj_to_dict(new_enrollment)

        service.create_enrollment(new_enrollment, enrollment_dict)

        return redirect(url_for("routes.enrollment_received"))

    return render_template("index.html")

@routes.route("/enrollments", methods=["GET"])
@login_required
def get_enrollments():
    enrollments = service.get_all_enrollments()

    return render_template("enrollments.html", enrollments=enrollments)

@routes.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
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

        enrollment_dict = service.obj_to_dict(new_enrollment)

        update = service.update_enrollment(enrollment, new_enrollment, enrollment_dict)

        if update:
            return redirect(url_for("routes.get_enrollments"))

@routes.route("/export-to-excel")
@login_required
def export_enrollments():
    app = current_app._get_current_object()
    output = service.export_to_excel(app)

    return send_file(output, as_attachment=True, download_name="incricoes.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@routes.route("/enrollment_received")
def enrollment_received():
    return render_template("enrollment_received.html")

@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")

        if password == os.getenv("ADMIN_PASSWORD"):
            session["logged_in"] = True
            return redirect("/enrollments")
    
    return render_template("login.html")

@routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.login"))

@routes.route("/export-to-telegram")
def export_to_telegram():
    service._thread_export_excel_to_telegram()
    
    return redirect(url_for("routes.get_enrollments"))
