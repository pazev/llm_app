# Project Context

A Streamlit chatbot for business managers and directors, backed by OpenAI via LangChain.
Every message and feedback event is persisted to a database for inspection and improvement.

---

## Architecture

```
streamlit.py          ← entry point, navigation, controller wiring
pages/                ← one .py per page; auto-discovered and sorted by PRIORITY
controllers/          ← orchestration layer; owns session lifecycle and DTO validation
services/             ← LLM abstraction (ChatService ABC); stub and OpenAI implementations
tools/                ← LangChain tools exposed to the LLM via bind_tools()
  __init__.py         ← ALL_TOOLS list; import and register every tool here
  _template.py        ← copy this to create a new tool
repositories/         ← all SQL access; each repo takes a SQLAlchemy Session
schemas/              ← Pydantic DTOs: *Create / *Submit for input, *Response for output
db/
  base.py             ← engine + Base; calls load_dotenv() at import time
  session.py          ← SessionLocal + get_db() context manager
  models/             ← SQLAlchemy ORM models
migrations/           ← Alembic; env.py reads DATABASE_URL from environment
```

### Key design rules

- **Tools are a service dependency**: `tools/__init__.py` exports `ALL_TOOLS`. The service layer (e.g. `OpenAILangChainService`) binds them via `llm.bind_tools(ALL_TOOLS)`. Tools must never import from `services/` or `controllers/` (no upward imports).
- **One tool per file**: each file in `tools/` defines exactly one `@tool` function and its Pydantic input schema. Register it in `tools/__init__.py`.
- **Docstring is the contract**: the `@tool` function's docstring becomes the description sent to the LLM — keep it precise and unambiguous.


- **Layers never bypass each other**: pages talk only to the controller; the controller talks to services and repositories; repositories talk only to the DB.
- **Session-per-operation**: `get_db()` is called inside each controller method. Sessions are never stored in Streamlit session_state or passed between layers.
- **DTOs are the contract**: the controller validates all inputs with Pydantic before touching the DB, and always returns Pydantic `*Response` objects — SQLAlchemy models never leave the controller.
- **No DB-level validation constraints**: type and value validation (e.g. sender must be "user" or "llm") lives in Pydantic schemas, not in the DB schema. Foreign keys are kept as structural integrity.
- **Environment**: `db/base.py` loads `.env` at import time, so `DATABASE_URL` is always available regardless of import order. Do not add a second `load_dotenv()` call elsewhere.

---

## Domain models

| Model | Key fields |
|---|---|
| `Conversation` | `conversation_id`, `datetime_start`, `title` |
| `Message` | `message_id`, `conversation_id`, `sender` ("user"/"llm"), `content`, `datetime` |
| `MessageFeedback` | `message_feedback_id`, `message_id`, `positive_feedback`, `comment`, `datetime` |

One `MessageFeedback` per `Message`, enforced via repository upsert logic (not a DB constraint).

---

## Adding a new page

1. Copy `pages/_template.py` to a new file, e.g. `pages/my_page.py`
2. Set `PAGE_NAME`, `SECTION_NAME`, `URL_PATH`, `PRIORITY`
3. Implement `build_page()`
4. Access the controller via `st.session_state["controller"]`

### Page navigation

Always use `load_page_urls()` for programmatic navigation — never hardcode `"pages/foo.py"` strings:

```python
from pages import load_page_urls

st.switch_page(load_page_urls()["chat"])
```

---

## Environment variables (`.env`)

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string (default: `sqlite:///./app.db`) |
| `OPENAI_API_KEY` | Required when `LLM_SERVICE=openai` |
| `LLM_SERVICE` | `stub` (default) or `openai` |
| `APP_ENV` | `development` / `production` |

To switch databases, change `DATABASE_URL` to a Postgres or MySQL connection string and run `alembic upgrade head`.

---

## Package management

Use `conda install -c conda-forge <package>` for all dependencies in this project.
