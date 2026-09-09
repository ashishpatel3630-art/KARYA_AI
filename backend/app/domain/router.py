from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.ai_adapter import answer_question, ingest_document
from app.core.database import get_db
from app.models.domain import Activity, Agent, Document, Task
from app.models.user import User
from app.schemas.domain import AgentCreate, ChatRequest, TaskCreate, TaskStatusUpdate


router = APIRouter(prefix="/api", tags=["Operations"])
UPLOAD_ROOT = Path("storage/uploads")
ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024


def _activity(db: Session, user: User, kind: str, entity: str, description: str):
    db.add(Activity(user_id=user.id, type=kind, entity=entity, description=description))


def _process_document(document_id: str):
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        document = db.scalar(select(Document).where(Document.id == document_id))
        if document is None:
            return
        document.status = "PROCESSING"
        db.commit()
        ingest_document(document.storage_path, document.id)
        document.status = "READY"
        document.processing_error = None
        db.commit()
    except Exception as exc:
        document = db.scalar(select(Document).where(Document.id == document_id))
        if document is not None:
            document.status = "FAILED"
            document.processing_error = str(exc)[:2000]
            db.commit()
    finally:
        db.close()


@router.get("/agents")
def list_agents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Agent).where(Agent.user_id == user.id).order_by(Agent.created_at.desc())).all()


@router.post("/agents", status_code=status.HTTP_201_CREATED)
def create_agent(data: AgentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = Agent(user_id=user.id, **data.model_dump())
    db.add(agent)
    _activity(db, user, "AGENT", agent.name, "Agent created.")
    db.commit()
    db.refresh(agent)
    return agent


@router.get("/tasks")
def list_tasks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc())).all()


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.agent_id and db.scalar(select(Agent).where(Agent.id == data.agent_id, Agent.user_id == user.id)) is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    task = Task(user_id=user.id, **data.model_dump())
    db.add(task)
    _activity(db, user, "TASK", task.title, "Task created and queued.")
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}")
def update_task(task_id: str, data: TaskStatusUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if data.status not in {"QUEUED", "CANCELLED"}:
        raise HTTPException(status_code=422, detail="Only queued and cancelled states are available without a worker")
    task.status = data.status
    _activity(db, user, "TASK", task.title, f"Task marked {data.status.lower()}.")
    db.commit()
    db.refresh(task)
    return task


@router.get("/documents")
def list_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc())).all()


@router.post("/documents/upload", status_code=status.HTTP_201_CREATED)
def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="File type is not supported.")
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    document_id = str(uuid4())
    path = UPLOAD_ROOT / f"{document_id}-{Path(file.filename or 'upload').name}"
    content = file.file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is too large. Maximum size is 25 MB.")
    path.write_bytes(content)
    document = Document(id=document_id, user_id=user.id, name=file.filename or path.name, content_type=file.content_type, storage_path=str(path), size_bytes=len(content))
    db.add(document)
    _activity(db, user, "DOCUMENT", document.name, "Document uploaded. Processing has not started because no worker is configured.")
    db.commit()
    db.refresh(document)
    background_tasks.add_task(_process_document, document.id)
    return document


@router.get("/documents/{document_id}")
def get_document(document_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user.id))
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/chat")
def chat(data: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owned_documents = db.scalars(select(Document).where(Document.user_id == user.id, Document.status == "READY")).all()
    requested_ids = data.document_ids or [document.id for document in owned_documents]
    allowed_ids = {document.id for document in owned_documents}
    if any(document_id not in allowed_ids for document_id in requested_ids):
        raise HTTPException(status_code=404, detail="One or more documents are not ready or not available")
    try:
        response = answer_question(data.message, requested_ids)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"RAG service unavailable: {exc}") from exc
    return {
        "answer": response.answer,
        "sources": [
            {
                "document_id": citation.document_id,
                "document_name": citation.file_name,
                "file_type": citation.file_type,
                "page": citation.page_number,
                "chunk_id": citation.chunk_id,
                "score": citation.similarity,
            }
            for citation in response.citations
        ],
    }


@router.get("/activity")
def list_activity(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Activity).where(Activity.user_id == user.id).order_by(Activity.created_at.desc())).all()