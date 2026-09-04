-- Esquema SQL de ejemplo para migrar inscripciones a una base relacional
-- Compatible con PostgreSQL y fácilmente adaptables a SQLite/MySQL

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE registrations (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    level VARCHAR(10) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending_confirmation',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT unique_student_course_level UNIQUE (student_id, course_id, level)
);

-- Datos de ejemplo para `courses`
INSERT INTO courses (code, name) VALUES
('ingles', 'Inglés'),
('frances', 'Francés'),
('aleman', 'Alemán')
ON CONFLICT (code) DO NOTHING;

-- Índices recomendados
CREATE INDEX IF NOT EXISTS idx_registrations_created_at ON registrations(created_at);
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);
