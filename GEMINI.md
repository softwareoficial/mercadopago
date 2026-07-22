# GEMINI.md - Project Guidelines for AI Agents

This project is a **Multi-Tenant Payment Gateway Platform** utilizing the Command Pattern.

## 1. Core Architectural Mandates
- **Command Pattern**: All business logic must be encapsulated in `Command` objects within `src/commands/`.
- **Interface Agnostic**: Core logic (`src/core/`) and Commands (`src/commands/`) must NOT depend on any specific interface (API, CLI, or Web). They should receive data and return results.
- **Multi-Tenancy**: Every payment operation must be scoped by a `client_id`. The system must fetch the corresponding Mercado Pago credentials from the database for each request.
- **Database First**: Use SQLAlchemy for all database interactions. Ensure models are defined in `src/core/models/models.py`.

## 2. Coding Standards
- **Language**: Python 3.10+.
- **Typing**: Use strict type hints for all function signatures.
- **Error Handling**: Use custom exception classes for business errors. Do not return generic `None` values for failures.
- **Documentation**: All new functions must have Google-style docstrings.

## 3. Workflow for adding a new Feature/Command
1.  **Update Model**: If the feature requires new data, update `src/core/models/models.py`.
2.  **Update Service**: If it requires a new external API call, update `src/core/services/mp_service.py`.
3.  **Create Command**: Create a new command class in the appropriate `src/commands/` subdirectory.
4.  **Register Command**: Add the command to `src/commands/registry.py`.
5.  **Expose Interface**: Add the corresponding route in `src/interfaces/api/routes.py` or argument in `src/interfaces/cli/cli_app.py`.

## 4. File Organization
- `src/core/services/`: Wrappers for external APIs.
- `src/core/models/`: SQLAlchemy models.
- `src/commands/`: Business logic orchestrators.
- `src/interfaces/`: Delivery mechanisms (API, CLI, Web).
