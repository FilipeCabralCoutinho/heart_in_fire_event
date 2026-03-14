import re
from typing import Optional

from email_validator import EmailNotValidError, validate_email
from flask import flash

ACCEPTED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
CHURCHS_NAMES = {
    "Congregação em Parque Alian",
    "Frente Miss Areia Branca",
    "Frente Miss Jardim José Bonifácio",
    "Igreja de Belford Roxo",
    "Igreja de Coelho da Rocha",
    "Igreja de Éden",
    "Igreja de Jardim América",
    "Igreja de Pq São José",
    "Igreja de Praça da Bandeira",
    "Igreja de São João de Meriti",
    "Igreja de Vila Humaitá",
    "Igreja de Vila Jurandir",
    "Igreja de Vila Tiradentes",
    "Igreja de Vilar do Teles",
}


class Validator:
    def cpf(self, cpf: str) -> bool:
        cpf = re.sub(r"\D", "", cpf)

        if len(cpf) != 11:
            return False

        if cpf == cpf[0] * 11:
            return False

        sum_count = sum(int(cpf[i]) * (10 - i) for i in range(9))
        dig1 = (sum_count * 10 % 11) % 10

        sum_count = sum(int(cpf[i]) * (11 - i) for i in range(10))
        dig2 = (sum_count * 10 % 11) % 10

        return dig1 == int(cpf[9]) and dig2 == int(cpf[10])

    def phone(self, phone: str) -> bool:
        phone = re.sub(r"\D", "", phone)

        if len(phone) not in (10, 11):
            return False

        return True

    def file(self, filename: str) -> bool:
        if filename is None:
            return True

        if "." not in filename:
            return False

        ext = filename.rsplit(".", 1)[1].lower()
        return ext in ACCEPTED_EXTENSIONS

    def church(self, church_name: str) -> bool:
        return church_name in CHURCHS_NAMES

    def name(self, name: str) -> bool:
        pattern = r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$"
        return bool(re.match(pattern, name))

    def email_format(self, email: str) -> bool:
        try:
            validate_email(email, check_deliverability=False)
            return True

        except EmailNotValidError:
            return False

    def validate_all(
        self,
        name: str,
        cpf: str,
        celphone: str,
        emergency_contact: str,
        email: str,
        church: str,
        filename: Optional[str] = None,
    ):
        if not self.name(name):
            flash(
                "O nome não pode conter números ou símbolos. Apenas letras e espaços são permitidos."
            )
            return False

        if not self.cpf(cpf):
            flash("CPF inválido!")
            return False

        if not self.phone(celphone):
            flash("Celular inválido!")
            return False

        if not self.phone(emergency_contact):
            flash("Contato de Emergência inválido!")
            return False

        if not self.email_format(email):
            flash("Email inválido. O formato deve ser: nome@dominio.com")
            return False

        if not self.file(filename):
            flash("Tipo de arquivo não permitido!")
            return False

        if not self.church(church):
            flash("A igreja informada é inválida")
            return False

        return None


validator = Validator()
