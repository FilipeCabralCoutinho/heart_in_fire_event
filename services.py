import io
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from threading import Thread

import pandas as pd
import requests
from dotenv import load_dotenv
from flask import current_app
from jinja2 import Template
from sqlalchemy import or_

from db import db
from logger import logger
from models import Enrollment

load_dotenv()

ROOT_PATH = Path(__file__).resolve().parent


class Service:
    def create_enrollment(self, new_enrollment):
        enrollment_cpf = new_enrollment.cpf
        enrollment_name = new_enrollment.name

        existing = (
            db.session.query(Enrollment)
            .filter(
                or_(
                    Enrollment.cpf == enrollment_cpf,
                    Enrollment.name == enrollment_name,
                )
            )
            .first()
        )

        if existing is not None:
            if existing.cpf == enrollment_cpf:
                logger.error(
                    f"Participant already registered. Name: {enrollment_name}"
                )
                return False

        logger.info(
            f"create_enrollment method initialized for Name: {enrollment_name}"
        )

        try:
            db.session.add(new_enrollment)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            logger.error(
                "Error when trying to save registration in the database. Name:"
                f" {enrollment_name}. Error: {e}"
            )
            raise

        enrollment = (
            db.session.query(Enrollment).filter_by(cpf=enrollment_cpf).first()
        )
        enrollment_dict = self.obj_to_dict(enrollment)

        self._send_notifications(enrollment_dict, "new")

        return True

    def get_all_enrollments(self):
        logger.info("get_all_enrollments method initialized!")

        try:
            enrollments = db.session.query(Enrollment).all()

        except Exception as e:
            logger.error(
                f"error when trying to get the registrations. Error: {e}"
            )
            raise

        return enrollments

    def make_dir(self, cpf, archive_name):
        logger.info(
            f"make_dir method initialized for archive: {archive_name}"
        )

        user_path = f"{ROOT_PATH}/uploads/{cpf}"
        os.makedirs(user_path, exist_ok=True)

        return os.path.join(user_path, archive_name)

    def update_enrollment(self, enrollment, new_enrollment, enrollment_dict):
        logger.info(f"update_enrollment initialized for id: {enrollment.id}")

        try:
            enrollment.name = new_enrollment.name
            enrollment.cpf = new_enrollment.cpf
            enrollment.church = new_enrollment.church
            enrollment.celphone = new_enrollment.celphone
            enrollment.emergency_contact = new_enrollment.emergency_contact
            enrollment.email = new_enrollment.email
            enrollment.remedy = new_enrollment.remedy
            enrollment.hour_remedy = new_enrollment.hour_remedy
            enrollment.payment_status = new_enrollment.payment_status

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            logger.error(
                "Error when trying to update enrollment"
                f" id: {enrollment.id}. Error: {e}"
            )
            raise

        self._send_notifications(enrollment_dict, "update")

        return True

    def export_to_excel(self, app):
        logger.info("export_to_excel method initialized!")

        with app.app_context():
            enrollments = db.session.query(Enrollment).all()

        data = []

        for i in enrollments:
            data.append(
                {
                    "ID": i.id,
                    "Nome": i.name,
                    "CPF": i.cpf,
                    "Igreja": i.church,
                    "Celular": i.celphone,
                    "Contato Emergência": i.emergency_contact,
                    "Email": i.email,
                    "Toma Remédio": i.remedy,
                    "Horário Remédio": i.hour_remedy,
                    "Status Pagamento": i.payment_status,
                    "Local Comprovante": i.local_proof,
                    "Data/Hora": str(i.created_at),
                    "Consentimento": i.consent_given,
                    "IP_USER": i.ip_address,
                }
            )

        df = pd.DataFrame(data)

        output = io.BytesIO()

        df.to_excel(output, index=False)

        output.seek(0)

        logger.info("Excel obtained with success!")

        return output

    def send_to_email(self, enrollment, type_msg):
        enrollment_id = enrollment.get("id")

        logger.info(
            "send_to_email method initialized for id:"
            f" {enrollment_id} and type_msg: {type_msg}"
        )

        msg = EmailMessage()

        if type_msg == "new":
            msg["Subject"] = (
                "Sua Inscrição foi recebida! - Retiro do Coração Abrasado"
            )

            text_head = "Confirmação de inscrição"

            text_title = "Recebemos sua inscrição 🙌"

            start_text = (
                """
                Sua inscrição para o <strong>Retiro do Coração Abrasado</strong> foi recebida.
                Assim que seu pagamento for confirmado por um dos organizadores você receberá
                um novo e-mail informando a confirmação.<br>
                Em breve nos vemos no <strong>Retiro do Coração Abrasado</strong> ❤️‍🔥
                """
                )

        elif type_msg == "update":
            msg["Subject"] = (
                "Confirmação de inscrição – Retiro do Coração Abrasado"
            )

            text_head = "Atualização de inscrição"

            text_title = "Sua Inscrição foi Atualizada ✅"

            start_text = (
                """
                Sua inscrição para o <strong>Retiro do Coração Abrasado</strong> foi atualizada.
                Os dados abaixo refletem o status atual da sua inscrição.<br>
                Mal posso esperar pra te encontrar no <strong>Retiro do Coração Abrasado</strong> ❤️‍🔥
                """
                )

        try:
            with open("templates/enrollment_email.html") as f:
                template = Template(f.read())

            html_email = template.render(
                enrollment=enrollment,
                text_head=text_head,
                text_title=text_title,
                start_text=start_text,
                organizer_1=os.getenv("ORGANIZER_1"),
                organizer_2=os.getenv("ORGANIZER_2"),
                organizer_3=os.getenv("ORGANIZER_3"),
            )

            msg.add_alternative(html_email, subtype="html")

            msg["From"] = (
                f"Retiro Coração Abrasado <{os.getenv('GMAIL_ADRESS')}>"
            )
            msg["To"] = enrollment.get("email")

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(
                    os.getenv("GMAIL_ADRESS"), os.getenv("GMAIL_PASSWORD_APP")
                )
                smtp.send_message(msg)

            logger.info(
                "Email sended with success for id:"
                f" {enrollment_id} and type_msg: {type_msg}"
            )

        except Exception as e:
            logger.error(
                "Error when trying to send email for"
                f" id: {enrollment_id} and type_msg: {type_msg}. Error: {e}"
            )
            raise

    def send_to_telegram(self, enrollment, type_msg):
        enrollment_id = enrollment.get("id")

        logger.info(
            "send_to_telegram method initialized for id:"
            f" {enrollment_id} and type_msg: {type_msg}"
        )

        message = f"""

            NR INSCR: {enrollment_id}
            NOME: {enrollment.get('name')}
            CPF: {enrollment.get('cpf')}
            IGREJA: {enrollment.get('church')}
            CELULAR: {enrollment.get('celphone')}
            CTT EMERGÊNCIA: {enrollment.get('emergency_contact')}
            EMAIL: {enrollment.get('email')}
            TOMA REMÉDIO: {enrollment.get('remedy')}
            HORÁRIO REMÉDIO: {enrollment.get('hour_remedy')}
            STATUS PAGAMENTO: {enrollment.get('payment_status')}

            """

        if type_msg == "new":
            message = "NOVA INSCRIÇÃO: " + message

            url = os.getenv("URL_TELEGRAM_SEND_MSG") + message

            try:
                logger.info(
                    "Initialize send msg with new enrollment id:"
                    f" {enrollment_id}"
                )
                response_msg = requests.post(url)
                response_msg.raise_for_status()

            except Exception as e:
                logger.error(
                    "Error when trying send telegram msg with id:"
                    f" {enrollment_id} and type_msg{type_msg}. Error: {e}"
                )
                raise e

            archive_type = os.path.splitext(enrollment.get("local_proof"))[1]

            if archive_type == ".pdf":
                url_proof = os.getenv("URL_TELEGRAM_SEND_DOC")
                key = "document"
            else:
                url_proof = os.getenv("URL_TELEGRAM_SEND_IMG")
                key = "photo"

            with open(enrollment.get("local_proof"), "rb") as proof:
                try:
                    logger.info(
                        f"Initialize send proof for id: {enrollment_id}"
                    )
                    response_proof = requests.post(
                        url_proof,
                        data={
                            "chat_id": os.getenv("ID_GRUPO_INSCRICOES"),
                            "caption": ("Comprovante inscrição"
                                        f" Nr {enrollment_id}"),
                        },
                        files={key: proof},
                    )

                    response_proof.raise_for_status()

                except Exception as e:
                    logger.error(
                        "Error when trying send proof"
                        f" for id: {enrollment_id}"
                    )
                    raise e

        elif type_msg == "update":
            message = "INSCRIÇÃO ATUALIZADA: " + message

            url = os.getenv("URL_TELEGRAM_SEND_MSG") + message

            try:
                logger.info(
                    "Initialize send msg with enrollment update"
                    f" for id: {enrollment_id}"
                )
                response_msg = requests.post(url)
                response_msg.raise_for_status()

            except Exception as e:
                logger.error(
                    "Error when trying send telegram msg for id:"
                    f" {enrollment_id} and type_msg: {type_msg}. Error{e}"
                )
                raise e

        logger.info(
            "Telegram messages sended with success for id:"
            f" {enrollment_id} and type_msg: {type_msg}"
        )

    def obj_to_dict(self, enrollment):
        logger.info(f"obj_to_dict initialized for id: {enrollment.id}")

        data = {
            "id": enrollment.id,
            "name": enrollment.name,
            "cpf": enrollment.cpf,
            "church": enrollment.church,
            "celphone": enrollment.celphone,
            "emergency_contact": enrollment.emergency_contact,
            "email": enrollment.email,
            "remedy": enrollment.remedy,
            "hour_remedy": enrollment.hour_remedy,
            "payment_status": enrollment.payment_status,
            "local_proof": enrollment.local_proof,
        }

        return data

    def _send_notifications(self, enrollment_dict, type_msg):
        enrollment_id = enrollment_dict.get("id")

        logger.info(
            f"_send_notifications initialized for id: {enrollment_id}"
        )

        try:
            Thread(
                target=self.send_to_email, args=(enrollment_dict, type_msg)
            ).start()

            Thread(
                target=self.send_to_telegram, args=(enrollment_dict, type_msg)
            ).start()

            logger.info(
                f"Threads created with success for id: {enrollment_id}"
            )

        except Exception as e:
            logger.error(
                f"Error when trying create Thread for id: {enrollment_id}"
            )
            raise e

    def export_excel_to_telegram(self, app):
        archive = self.export_to_excel(app)

        try:
            logger.info("Initialize send enrollments excel to telegram.")
            response = requests.post(
                os.getenv("URL_TELEGRAM_SEND_DOC"),
                data={
                    "chat_id": os.getenv("ID_GRUPO_INSCRICOES"),
                    "caption": "Arquivo Consolidação Inscrições",
                },
                files={"document": ("inscricoes.xlsx", archive)},
            )

            response.raise_for_status()

        except Exception as e:
            logger.error(
                "Error when trying send enrollments excel to telegram."
                f" Error:  {e}"
            )
            raise e

    def _thread_export_excel_to_telegram(self):
        logger.info("_thread_export_excel_to_telegram method initialized!")
        try:
            Thread(
                target=self.export_excel_to_telegram,
                args=(current_app._get_current_object(),),
            ).start()

            logger.info("Thread created with success!")

        except Exception as e:
            logger.error(
                "Error when trying create thread for "
                f"export_excel_to_telegram. Error: {e}"
            )
            raise e
