```mermaid
erDiagram
    STUDENTS {
        INTEGER id PK "Auto-increment"
        VARCHAR name
        VARCHAR email "Único"
    }
    COURSES {
        INTEGER id PK
        VARCHAR code "ingles|frances|aleman"
        VARCHAR name
    }
    REGISTRATIONS {
        INTEGER id PK
        INTEGER student_id FK
        INTEGER course_id FK
        VARCHAR level
        VARCHAR status
        TIMESTAMP created_at
    }

    STUDENTS ||--o{ REGISTRATIONS : "has"
    COURSES ||--o{ REGISTRATIONS : "offers"
```

Descripción breve
-----------------
- `STUDENTS`: almacena datos personales básicos. `email` debe indexarse y, preferiblemente, ser único.
- `COURSES`: lista de idiomas/servicios ofrecidos (Inglés, Francés, Alemán).
- `REGISTRATIONS`: registro de inscripciones; relaciona `students` con `courses`, incluye `level` y `status`.
