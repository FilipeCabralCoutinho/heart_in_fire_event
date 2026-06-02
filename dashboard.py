from db import db
from models import Enrollment

def get_dashboard_data():
    # Example: Fetch some data from the database
    data = db.session.query(Enrollment).all()
    return data

def count_numbers():
    total = db.session.query(Enrollment).count()
    total_confirmed = db.session.query(Enrollment).filter_by(payment_status='CONFIRMADO').count()
    total_pending = db.session.query(Enrollment).filter_by(payment_status='PENDENTE').count()
    
    sao_joao = db.session.query(Enrollment).filter_by(church='Igreja de São João de Meriti').count()
    areia_branca = db.session.query(Enrollment).filter_by(church='Frente Miss Areia Branca').count()
    parque_alian = db.session.query(Enrollment).filter_by(church='Congregação em Parque Alian').count()
    belford_roxo = db.session.query(Enrollment).filter_by(church='Igreja de Belford Roxo').count()
    coelho_da_rocha = db.session.query(Enrollment).filter_by(church='Igreja de Coelho da Rocha').count()
    eden = db.session.query(Enrollment).filter_by(church='Igreja de Éden').count()
    jardim_america = db.session.query(Enrollment).filter_by(church='Igreja de Jardim América').count()
    pq_sao_jose = db.session.query(Enrollment).filter_by(church='Igreja de Pq São José').count()
    praca_da_bandeira = db.session.query(Enrollment).filter_by(church='Igreja de Praça da Bandeira').count()
    vila_humaita = db.session.query(Enrollment).filter_by(church='Igreja de Vila Humaitá').count()
    jose_bonifacio = db.session.query(Enrollment).filter_by(church='Frente Miss Jardim José Bonifácio').count()
    vila_jurandir = db.session.query(Enrollment).filter_by(church='Igreja de Vila Jurandir').count()
    vila_tiradentes = db.session.query(Enrollment).filter_by(church='Igreja de Vila Tiradentes').count()
    vilar_do_teles = db.session.query(Enrollment).filter_by(church='Igreja de Vilar do Teles').count()
    vila_formoso = db.session.query(Enrollment).filter_by(church='Congregação em Vila Formoso').count()
    
    total_dict = {
        "total": total,
        "total_confirmed": total_confirmed,
        "total_pending": total_pending,
        "sao_joao": sao_joao,
        "areia_branca": areia_branca,
        "parque_alian": parque_alian,
        "belford_roxo": belford_roxo,
        "coelho_da_rocha": coelho_da_rocha,
        "eden": eden,
        "jardim_america": jardim_america,
        "pq_sao_jose": pq_sao_jose,
        "praca_da_bandeira": praca_da_bandeira,
        "vila_humaita": vila_humaita,
        "jose_bonifacio": jose_bonifacio,
        "vila_jurandir": vila_jurandir,
        "vila_tiradentes": vila_tiradentes,
        "vilar_do_teles": vilar_do_teles,
        "vila_formoso": vila_formoso
    }
    return total_dict
