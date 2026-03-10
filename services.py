from db import db
from models import Enrollment
from pathlib import Path
import os

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
    
    def update_enrollment(self, id):
        pass



    def save_proof(self):
        pass

    def send_to_email(self):
        pass

    def send_to_telegram(self):
        pass
