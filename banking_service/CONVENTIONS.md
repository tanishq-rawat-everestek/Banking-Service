# FastAPI Skeleton Conventions

This document outlines the coding standards and file structures for this FastAPI project.
Read these rules carefully and use them verbatim when generating new code.

## Folder Layout
- `ai/agilery/app/models/`: SQLModel ORM entity classes (inherit from `SQLModel, table=True`).
- `ai/agilery/app/enums/`: Python `str, Enum` classes for status/type fields.
- `ai/agilery/app/schemas/`: Pydantic DTOs using `CamelModel` from `fastapi_camelcase` (Base, Create, Update, Patch, Response per entity).
- `ai/agilery/app/repositories/`: Database access logic via SQLModel `Session`. Use `Depends(get_db)` for injection.
- `ai/agilery/app/mappers/`: Stateless functions translating Entities ↔ DTOs. No DB access.
- `ai/agilery/app/services/`: Core business logic. Owns transaction lifecycle (`commit`/`rollback`). Uses `ResourceNotFoundException`, `ValidationException`, `ProcessingException` from `app.exceptions`.
- `ai/agilery/app/validation/`: Cross-field and business rule validation classes (in `ai/agilery/app/validation/service/`).
- `ai/agilery/app/controllers/`: FastAPI routers and dependency injection. One router per resource.
- `ai/agilery/app/exceptions/`: Custom exception classes and global exception handlers.
- `ai/agilery/app/security/`: JWT utilities (`ai/agilery/app/security/jwt.py`) and user helpers.
- `ai/agilery/app/db/`: `session.py` (provides `get_db()` generator) and `init_db.py` (creates tables via `SQLModel.metadata.create_all`).
- `ai/agilery/app/utils/`: Shared helpers (e.g., `audit.py` for applying audit fields).

## Naming Patterns
- **Files:** snake_case (e.g., `product_repository.py`, `product_service.py`)
- **Classes:** PascalCase (e.g., `ProductRepository`, `ProductService`)
- **Functions/Methods:** snake_case (e.g., `get_by_id`, `create_product`)

## Imports
- Use explicit root-relative imports (e.g., `from ai.agilery.app.models.product import Product`)
- Do not use relative imports like `from .product import Product`
- Place standard library imports first, followed by third-party, and then local app imports.

## Database / ORM
- All ORM models inherit from `SQLModel` with `table=True`. No separate `Base` class is needed.
- DB sessions are provided via `from ai.agilery.app.db.session import get_db` using FastAPI `Depends()`.
- The session commits are handled in the **service layer**. Repositories call `flush()` only.

## DTOs / Schemas
- All DTOs inherit from `CamelModel` (from `fastapi_camelcase`). Every entity has 5 DTO classes: Base, Create, Update, Patch, Response.
- All Response DTOs include `id`, audit fields (`created_date_time`, `last_modified_date_time`, `created_by`, `modified_by`) marked as `readOnly`.

## Exception Handling
- Use `ResourceNotFoundException` for 404s, `ValidationException` for business rule failures, `ProcessingException` for unexpected server errors.
- Do NOT raise raw `HTTPException` in service or repository layers.

## Docstring Style
- Use Google-style docstrings for any non-trivial classes or methods. Do not over-document obvious functionality.
