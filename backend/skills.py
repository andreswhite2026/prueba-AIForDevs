# backend/skills.py
import json
import os

REGISTRATIONS_FILE = "student_registrations.json"

def register_student_skill(name: str, course: str, level: str, email: str) -> str:
    """Registra formalmente a un estudiante guardando los datos en un archivo JSON local."""
    new_record = {
        "name": name,
        "course": course,
        "level": level,
        "email": email
    }
    
    data = []
    if os.path.exists(REGISTRATIONS_FILE):
        try:
            with open(REGISTRATIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
            
    data.append(new_record)
    with open(REGISTRATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    return f"Estudiante {name} registrado con éxito en el curso de {course} ({level}). Registro guardado localmente."

def convert_currency_skill(amount_cop: float) -> str:
    """Convierte un valor en pesos colombianos (COP) a dólares estadounidenses (USD) de forma estimada."""
    # Tasa de cambio simulada de referencia
    tasa_cambio = 4000.0 
    amount_usd = round(amount_cop / tasa_cambio, 2)
    return f"${amount_cop:,.0f} COP equivalen aproximadamente a ${amount_usd:,.2f} USD (Tasa estimada)."