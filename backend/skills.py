"""Deterministic local skills for the academy application."""

import json
import os
import re
import tempfile
import threading
import unicodedata
import uuid
from datetime import datetime, timezone
from typing import Any


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRATIONS_FILE = os.path.join(BASE_DIR, "student_registrations.json")
REGISTRATION_LOCK = threading.Lock()

SUPPORTED_COURSES = {
    "ingles": "Inglés",
    "frances": "Francés",
    "aleman": "Alemán",
}
SUPPORTED_LEVELS = {"A1", "A2", "B1", "B2", "C1"}
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
NAME_PATTERN = re.compile(
    r"(?:me\s+llamo|mi\s+nombre\s+es|soy)\s+"
    r"([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+){1,3}?)"
    r"(?=\s*(?:,|;|\.|$|y\s+(?:quiero|deseo|mi\s+correo|correo|email)|(?:mi\s+)?(?:correo|email)))",
    re.IGNORECASE,
)


def _normalized(value: str) -> str:
    """Lowercase text without accents, for deterministic matching."""
    return "".join(
        char
        for char in unicodedata.normalize("NFD", value.lower())
        if unicodedata.category(char) != "Mn"
    )


def extract_registration_details(prompt: str) -> dict[str, str | None]:
    """Extract only enrollment fields explicitly supplied by the user."""
    normalized = _normalized(prompt)
    email_match = EMAIL_PATTERN.search(prompt)
    name_match = NAME_PATTERN.search(prompt)
    course = next(
        (label for keyword, label in SUPPORTED_COURSES.items() if re.search(rf"\b{keyword}\b", normalized)),
        None,
    )
    level_match = re.search(r"\b(a1|a2|b1|b2|c1)\b", normalized, re.IGNORECASE)

    return {
        "name": " ".join(name_match.group(1).split()).title() if name_match else None,
        "email": email_match.group(0).lower() if email_match else None,
        "course": course,
        "level": level_match.group(1).upper() if level_match else None,
    }


def missing_registration_fields(details: dict[str, str | None]) -> list[str]:
    labels = {
        "name": "nombre completo",
        "email": "correo electrónico",
        "course": "idioma (Inglés, Francés o Alemán)",
        "level": "nivel (A1, A2, B1, B2 o C1)",
    }
    return [label for field, label in labels.items() if not details.get(field)]


def registration_missing_data_message(missing_fields: list[str]) -> str:
    return (
        f"Para completar tu inscripción necesito: {', '.join(missing_fields)}. "
        "La información que ya compartiste queda pendiente durante esta conversación; "
        "no se creó ningún registro todavía. "
        "Ejemplo: “Quiero inscribirme; me llamo Ana Pérez, mi correo es "
        "ana@correo.com, quiero Francés nivel A1”."
    )


def _load_registrations() -> list[dict[str, Any]]:
    if not os.path.exists(REGISTRATIONS_FILE):
        return []
    try:
        with open(REGISTRATIONS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "El archivo de inscripciones contiene datos inválidos; no se modificó para evitar pérdida de información."
        ) from exc
    except OSError as exc:
        raise RuntimeError("No fue posible leer el archivo de inscripciones.") from exc
    if not isinstance(data, list):
        raise RuntimeError("El formato del archivo de inscripciones no es válido.")
    return data


def _write_registrations(registrations: list[dict[str, Any]]) -> None:
    """Atomically replace the JSON file, preventing partial writes."""
    file_descriptor, temporary_path = tempfile.mkstemp(
        dir=os.path.dirname(REGISTRATIONS_FILE),
        prefix=".student_registrations_",
        suffix=".json",
        text=True,
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as file:
            json.dump(registrations, file, indent=2, ensure_ascii=False)
            file.write("\n")
        os.replace(temporary_path, REGISTRATIONS_FILE)
    except OSError as exc:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass
        raise RuntimeError("No fue posible guardar la inscripción.") from exc


def register_student_skill(name: str, course: str, level: str, email: str) -> str:
    """Persist a validated enrollment and prevent duplicate same-level registrations."""
    name = " ".join(name.split()).title()
    course = SUPPORTED_COURSES.get(_normalized(course), course)
    level = level.upper().strip()
    email = email.lower().strip()

    if not name or len(name.split()) < 2:
        raise ValueError("Ingresa el nombre completo del estudiante.")
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("Ingresa un correo electrónico válido.")
    if course not in SUPPORTED_COURSES.values():
        raise ValueError("El idioma debe ser Inglés, Francés o Alemán.")
    if level not in SUPPORTED_LEVELS:
        raise ValueError("El nivel debe ser A1, A2, B1, B2 o C1.")

    with REGISTRATION_LOCK:
        registrations = _load_registrations()
        for record in registrations:
            if (
                str(record.get("email", "")).lower() == email
                and record.get("course") == course
                and str(record.get("level", "")).upper() == level
            ):
                return f"El correo {email} ya tiene una inscripción activa para {course}, nivel {level}."

        registrations.append(
            {
                "id": str(uuid.uuid4()),
                "name": name,
                "email": email,
                "course": course,
                "level": level,
                "status": "pending_confirmation",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        _write_registrations(registrations)

    return (
        f"Solicitud de inscripción registrada para {name}: {course}, nivel {level}. "
        f"Enviaremos la confirmación al correo {email}."
    )


def convert_currency_skill(amount_cop: float) -> str:
    """Convierte un valor en pesos colombianos a dólares estadounidenses (tasa estimada)."""
    tasa_cambio = 4000.0
    amount_usd = amount_cop / tasa_cambio
    return (
        f"El valor de ${amount_cop:,.0f} COP equivale aproximadamente a "
        f"${amount_usd:,.2f} USD (Tasa de referencia: 1 USD = ${tasa_cambio:,.0f} COP)."
    )
