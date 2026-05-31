from sqlalchemy import text
from db import db

def get_dashboard_data():
    # Example: Fetch some data from the database
    data = db.session.execute(text("SELECT * FROM enrollment")).fetchall()
    return data

def count_numbers():
    total = db.session.execute(text("SELECT COUNT(*) FROM enrollment")).fetchone()[0]
    total_confirmed = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE payment_status='CONFIRMADO'")).fetchone()[0]
    total_pending = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE payment_status='PENDENTE'")).fetchone()[0]
    sao_joao = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Igreja de São João de Meriti'")).fetchone()[0]
    areia_branca = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Frente Miss Areia Branca'")).fetchone()[0]
    parque_alian = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Congregação em Parque Alian'")).fetchone()[0]
    belford_roxo = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Igreja de Belford Roxo'")).fetchone()[0]
    coelho_da_rocha = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Igreja de Coelho da Rocha'")).fetchone()[0]
    eden = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Igreja de Éden'")).fetchone()[0]
    jardim_america = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Igreja de Jardim América'")).fetchone()[0]
    pq_sao_jose = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Igreja de Pq São José'")).fetchone()[0]
    praca_da_bandeira = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Igreja de Praça da Bandeira'")).fetchone()[0]
    vila_humaita = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Igreja de Vila Humaitá'")).fetchone()[0]
    jose_bonifacio = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Frente Miss Jardim José Bonifácio'")).fetchone()[0]
    vila_jurandir = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Igreja de Vila Jurandir'")).fetchone()[0]
    vila_tiradentes = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Igreja de Vila Tiradentes'")).fetchone()[0]
    vilar_do_teles = db.session.execute(text("SELECT COUNT(*) FROM enrollment WHERE church='Igreja de Vilar do Teles'")).fetchone()[0]
    total = {
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
        "vilar_do_teles": vilar_do_teles
    }
    return total
