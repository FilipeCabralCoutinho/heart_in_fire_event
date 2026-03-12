from db import db
from models import Enrollment
from pathlib import Path
import os
import pandas as pd
import io
import requests
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

ROOT_PATH = Path(__file__).resolve().parent


class Service:
    def __init__(self):
        self.queue_telegram = []

    def create_enrollment(self, new_enrollment):
        db.session.add(new_enrollment)
        db.session.commit()

        self.send_to_email()
        Thread(
        target=self.send_to_telegram,
        args=(new_enrollment, "new")
        ).start()

    def get_all_enrollments(self):
        enrollments = db.session.query(Enrollment).all()

        return enrollments
    
    def make_dir(self, cpf, archive_name):
        user_path = f"{ROOT_PATH}/uploads/{cpf}"
        os.makedirs(user_path, exist_ok=True)

        return os.path.join(user_path, archive_name)
    
    def update_enrollment(self, enrollment, new_enrollment):
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

        Thread(
        target=self.send_to_telegram,
        args=(new_enrollment, "update")
        ).start()

        return True

    def export_to_excel(self):
        enrollments = db.session.query(Enrollment).all()

        data = []

        for i in enrollments:
            data.append({
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
                "Local Comprovante": i.local_proof
            })

        df = pd.DataFrame(data)

        output = io.BytesIO()

        df.to_excel(output, index=False)

        output.seek(0)

        return output

    def send_to_email(self):
        pass

    def send_to_telegram(self, enrollment, type_msg):
        message = f"""
            
            NR INSCR: {enrollment.id}
            NOME: {enrollment.name}
            CPF: {enrollment.cpf}
            IGREJA: {enrollment.church}
            CELULAR: {enrollment.celphone}
            CTT EMERGÊNCIA: {enrollment.emergency_contact}
            EMAIL: {enrollment.email}
            TOMA REMÉDIO: {enrollment.remedy}
            HORÁRIO REMÉDIO: {enrollment.hour_remedy}
            STATUS PAGAMENTO: {enrollment.payment_status}
            
            """

        if type_msg == "new":
            message = "NOVA INSCRIÇÃO: " + message

            url = os.getenv("URL_TELEGRAM_SEND_MSG") + message

            try:
                response_msg = requests.post(url)
                response_msg.raise_for_status()

            except Exception as e:
                    raise e

            archive_type = os.path.splitext(enrollment.local_proof)[1]

            if archive_type == ".pdf":
                url_proof = os.getenv("URL_TELEGRAM_SEND_DOC")
                key = "document"
            else:
                url_proof = os.getenv("URL_TELEGRAM_SEND_IMG")
                key = "photo"

            with open(enrollment.local_proof, "rb") as proof:
                try:
                    response_proof = requests.post(
                        url_proof,
                        data={
                            "chat_id": os.getenv("ID_GRUPO_INSCRICOES"),
                            "caption": f"Comprovante inscrição Nr {enrollment.id}"
                        },
                        files={
                            key: proof
                        }
                    )

                    response_proof.raise_for_status()

                except Exception as e:
                    raise e

        elif type_msg == "update":
            message = "INSCRIÇÃO ATUALIZADA: " + message

            url = os.getenv("URL_TELEGRAM_SEND_MSG") + message

            try:
                response_msg = requests.post(url)
                response_msg.raise_for_status()

            except Exception as e:
                raise e
