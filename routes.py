from flask import render_template, request, Blueprint, redirect, url_for, send_file, session, current_app, flash
from services import Service
from models import Enrollment
from services import Service
import os
from auth import login_required
from db import db
from validator import validator
from logger import logger

routes = Blueprint("routes", __name__)

service = Service()

@routes.route("/", methods=["GET", "POST"])
def enrollment():
    if request.method == "POST":
        name = request.form.get("nomeForm")

        logger.info(f"A new registration process has been initiated for Name: {name}")

        consent_given = request.form.get("lgpdForm")

        if not consent_given:
            flash("É necessário concordar com os termo de consentimento para tratamento dos dados para fins do evento.")
            return redirect(url_for("routes.enrollment"))


        file = request.files.get("proofForm")
        cpf = request.form.get("cpfForm")
        celphone = request.form.get("celForm")
        emergency_contact = request.form.get("emergencyContactForm")
        email = request.form.get("emailForm")
        church = request.form.get("churchForm")

        valid = validator.validate_all(name, cpf, celphone, emergency_contact, email, church, file.filename)

        if valid is False:
            return redirect(url_for("routes.enrollment"))
        elif valid is not None:
            logger.critical(f"Fail in validation data, data informed: {valid}")
            return redirect(url_for("routes.enrollment"))

        logger.info(f"Information validated for the name {name}, proceeding with registration creation.")

        upload_path = service.make_dir(cpf, file.filename)

        file.save(upload_path)


        new_enrollment = Enrollment(
            name=name,
            cpf=cpf,
            church=church,
            celphone=celphone,
            emergency_contact=emergency_contact,
            email=email,
            remedy=request.form.get("remedyForm"),
            hour_remedy=request.form.get("hourForm"),
            local_proof=upload_path,
            payment_status="PENDENTE",
            consent_given=consent_given,
            ip_address=request.remote_addr
        )

        response = service.create_enrollment(new_enrollment)

        if response is False:
            flash("Participante já cadastrado!")
            return redirect(url_for("routes.enrollment"))

        logger.info(f"Registration completed for the name: {name}")

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
        name = request.form.get("nomeForm")

        logger.info(f"A update enrollment process has been initiated for id: {enrollment.id}")

        cpf = request.form.get("cpfForm")
        celphone = request.form.get("celForm")
        emergency_contact = request.form.get("emergencyContactForm")
        email = request.form.get("emailForm")
        church = request.form.get("churchForm")

        valid = validator.validate_all(name, cpf, celphone, emergency_contact, email, church)
        
        if valid is False:
            return redirect(url_for("routes.update_enrollments", id=enrollment.id))
        elif valid is not None:
            logger.critical(f"Fail in validation data, data informed: {valid}")
            return redirect(url_for("routes.enrollment"))

        logger.info(f"Information validated for the id {enrollment.id}, proceeding with update enrollment.")

        new_enrollment = Enrollment(
            id=enrollment.id,
            name=name,
            cpf=cpf,
            church=church,
            celphone=celphone,
            emergency_contact=emergency_contact,
            email=email,
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

@routes.route("/payment-pix")
def payment_pix():
    payment_link = os.getenv("PIX_URL")

    return redirect(payment_link)

@routes.route("/payment-credit-card")
def payment_credit_card():
    payment_link = os.getenv("CREDIT_CARD_URL")

    return redirect(payment_link)