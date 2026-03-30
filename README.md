# LLM Business Chatbot

A chatbot designed to provide business answers for managers and directors.

## How it works

### Running the project

```bash
# 1. activate your conda env
conda activate pyenvs

# 2. copy and fill in your env vars
cp .env.example .env

# 3. apply DB migrations (only needed first time, or after schema changes)
python manage.py init

# 4. run the app
python manage.py run
```

### Initialization flow

When `streamlit run streamlit.py` is executed:

```
streamlit.py imports
  └─ db/base.py               ← load_dotenv() runs, engine created, Base defined
  └─ services/__init__.py     ← reads LLM_SERVICE env var
  └─ controllers/chat_controller.py

streamlit.py executes (top-level code)
  └─ checks st.session_state["controller"]  (not set yet on first load)
      └─ _build_controller()
          └─ get_llm_service()  → returns StubLLMService or OpenAILangChainService
          └─ ChatController(chat_service=...)  stored in session_state

  └─ _load_page_modules()
      └─ scans pages/*.py, excludes __init__ and _template
      └─ imports each module, reads PRIORITY
      └─ sorts by PRIORITY ascending

  └─ builds st.navigation({section: [pages]})
  └─ nav.run()  → renders the current page
```

The controller is created **once per browser session** and cached in `st.session_state`. On every Streamlit rerun (button click, input, etc.) the top-level code runs again, but the controller is reused from state.

### Data flow

#### Starting a conversation

```
User clicks "New Conversation"
  └─ chat.py: controller.start_conversation()
      └─ ChatController:
          └─ ConversationCreate(title=None)       ← Pydantic validation
          └─ get_db()                             ← new session opened
              └─ ConversationRepository.create()
                  └─ INSERT into conversations
                  └─ session.flush()              ← assigns conversation_id
              └─ ConversationResponse.model_validate(conv)  ← ORM → Pydantic
          └─ session.commit() + session.close()  ← get_db() exits
      └─ returns ConversationResponse

  └─ chat.py: stores conversation_id in st.session_state
```

#### Sending a message

```
User types and submits a message
  └─ chat.py: controller.send_message(conversation_id, user_input, history)
      └─ ChatController:
          └─ MessageCreate(sender="user", content=...)   ← validates not empty
          └─ chat_service.get_response(content, history) ← calls LLM (or stub)
          └─ MessageCreate(sender="llm", content=...)    ← validates LLM response
          └─ get_db()                                    ← new session opened
              └─ MessageRepository.create(sender="user", ...)  ← INSERT
              └─ MessageResponse.model_validate(user_msg)
              └─ MessageRepository.create(sender="llm", ...)   ← INSERT
              └─ MessageResponse.model_validate(llm_msg)
          └─ session.commit() + session.close()
      └─ returns (MessageResponse, MessageResponse)

  └─ chat.py: appends both to st.session_state["messages"]
  └─ st.rerun() → page re-renders with new messages
```

Both messages are saved in a **single transaction** — if anything fails, neither is persisted.

#### Submitting feedback

```
User clicks 👍, 👎, or saves a comment
  └─ chat.py: controller.submit_feedback(message_id, positive_feedback=True/False/None, comment=...)
      └─ ChatController:
          └─ FeedbackSubmit(...)   ← validates at least one field is set
          └─ get_db()
              └─ FeedbackRepository.upsert()
                  └─ SELECT existing feedback for message_id
                  └─ INSERT if none, UPDATE if exists (partial: only non-None fields overwrite)
                  └─ session.flush()
              └─ FeedbackResponse.model_validate(feedback)
          └─ session.commit() + session.close()

  └─ chat.py: updates st.session_state[f"feedback_{message_id}"]
  └─ st.rerun()
```

### Architecture diagram

```
Browser
  │
  ▼
streamlit.py  (navigation shell, wires controller once)
  │
  ▼
pages/chat.py  (UI only — reads/writes st.session_state, calls controller)
  │
  ▼
ChatController  (validates input with Pydantic, owns DB session lifecycle)
  ├──► ChatService  (LLM call — stub or OpenAI/LangChain)
  └──► Repositories  (SQL via SQLAlchemy, one session per controller call)
          │
          ▼
        SQLite / Postgres / MySQL  (configured via DATABASE_URL)
```

---

## Stack

- **UI**: Streamlit with chat component and per-message feedback
- **Controller**: Python orchestration layer
- **Service Layer**: LangChain + OpenAI (stub service for development)
- **Database**: SQLAlchemy + Alembic (SQLite by default; switchable to MSSQL, MySQL, or PostgreSQL)

## Setup

1. Create and activate a conda environment:
   ```bash
   conda create -n pyenvs python=3.11
   conda activate pyenvs
   ```

2. Install dependencies:
   ```bash
   conda install -c conda-forge --file requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your values:
   ```bash
   cp .env.example .env
   ```

4. Run first-time initialisation (applies DB migrations):
   ```bash
   python manage.py init
   ```

5. Start the app:
   ```bash
   python manage.py run
   ```

## Project management (manage.py)

| Command | Description |
|---|---|
| `python manage.py run` | Start the Streamlit app |
| `python manage.py init` | Run first-time initialisation (applies Alembic migrations) |
| `python manage.py dumpzip` | Create a timestamped zip of the project in `./dumpzip/` |
| `python manage.py tree` | Print the project file tree |
| `python manage.py clear` | Remove cache and garbage files (`__pycache__`, `.pyc`, etc.) |
| `python manage.py trim_trailing_spaces` | Strip trailing whitespace from all text files |

## Adding a new page

1. Copy `pages/_template.py` to a new file under `pages/`
2. Fill in `PAGE_NAME`, `SECTION_NAME`, `URL_PATH`, `PRIORITY`, and implement `build_page()`
3. The page is auto-discovered — no registration needed

## Switching the LLM service

Change `LLM_SERVICE` in `.env`:
- `stub` — returns "Message Processed" (default for development)
- `openai` — uses LangChain + OpenAI

## Switching the database

Change `DATABASE_URL` in `.env` to a valid SQLAlchemy connection string:
- SQLite: `sqlite:///./app.db`
- PostgreSQL: `postgresql+psycopg2://user:pass@host/db`
- MySQL: `mysql+pymysql://user:pass@host/db`
- MSSQL: `mssql+pyodbc://user:pass@host/db?driver=ODBC+Driver+17+for+SQL+Server`

After switching, run `alembic upgrade head` to apply migrations to the new database.
