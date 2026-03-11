from db import db
from models import Enrollment
from pathlib import Path
import os
import pandas as pd
import io

ROOT_PATH = Path(__file__).resolve().parent


class Service:
    def create_enrollment(self, new_enrollment):
        db.session.add(new_enrollment)
        db.session.commit()

        self.send_to_email()
        self.send_to_telegram()

        return "OK"

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

    def send_to_telegram(self):
        pass
