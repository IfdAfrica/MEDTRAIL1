import os, uuid, hashlib, secrets
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, String, DateTime, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
import magic
from jose import jwt

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medtrail.db")
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "./storage"))
MAX_BYTES = int(os.getenv("MAX_FILE_SIZE_MB", "20")) * 1024 * 1024
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_THIS_IN_PRODUCTION")
ALGORITHM = "HS256"

ALLOWED = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

app = FastAPI(title="MEDTRAIL Secure Upload API", version="1.0.0")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class FileRecord(Base):
    __tablename__ = "files"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    patient_id: Mapped[str] = mapped_column(String(100), index=True)
    module: Mapped[str] = mapped_column(String(50), index=True)
    document_type: Mapped[str] = mapped_column(String(100))
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255), unique=True)
    mime_type: Mapped[str] = mapped_column(String(150))
    size: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    uploaded_by: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

Base.metadata.create_all(engine)

def require_user(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Autenticação obrigatória")
    token = authorization[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload["sub"]
    except Exception:
        raise HTTPException(401, "Token inválido")

def safe_original_name(name: str) -> str:
    name = Path(name or "arquivo").name
    return name[:255]

def extension(name: str) -> str:
    return Path(name).suffix.lower().lstrip(".")

def validate_module(module: str) -> None:
    allowed = {"BODY_TRAIL","CLINIC_TRAIL","FARMOTRAIL","SOCIAL_LIFESTYLE","LIFE_RISK","GENERAL"}
    if module not in allowed:
        raise HTTPException(400, "Módulo inválido")

@app.post("/api/auth/demo-token")
def demo_token():
    # SOMENTE PARA DESENVOLVIMENTO. Remover antes de produção.
    token = jwt.encode(
        {"sub":"demo-profissional","exp":datetime.now(timezone.utc)+timedelta(hours=1)},
        JWT_SECRET, algorithm=ALGORITHM
    )
    return {"access_token": token, "warning":"Endpoint de demonstração; substituir por IAM/OIDC em produção."}

@app.post("/api/files/upload")
async def upload_file(
    file: Annotated[UploadFile, File()],
    patient_id: Annotated[str, Form()],
    module: Annotated[str, Form()],
    document_type: Annotated[str, Form()],
    authorization: Annotated[str | None, Header()] = None,
):
    user = require_user(authorization)
    validate_module(module)

    original = safe_original_name(file.filename)
    ext = extension(original)
    if ext not in ALLOWED:
        raise HTTPException(415, "Tipo de ficheiro não permitido")

    # Ler em chunks para evitar carregar ficheiros grandes na memória.
    temp_id = uuid.uuid4().hex
    temp_path = STORAGE_DIR / f".upload-{temp_id}"
    size = 0
    sha = hashlib.sha256()

    try:
        with temp_path.open("wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(413, "Ficheiro excede o limite permitido")
                sha.update(chunk)
                out.write(chunk)

        detected = magic.from_file(str(temp_path), mime=True)
        if detected != ALLOWED[ext]:
            raise HTTPException(415, "Conteúdo não corresponde ao tipo declarado")

        file_id = str(uuid.uuid4())
        stored = f"{file_id}.{ext}"
        final_path = STORAGE_DIR / stored
        temp_path.replace(final_path)

        db = SessionLocal()
        try:
            record = FileRecord(
                id=file_id,
                patient_id=patient_id,
                module=module,
                document_type=document_type[:100],
                original_name=original,
                stored_name=stored,
                mime_type=detected,
                size=size,
                sha256=sha.hexdigest(),
                uploaded_by=user,
                created_at=datetime.now(timezone.utc),
            )
            db.add(record)
            db.commit()
        finally:
            db.close()

        return {
            "success": True,
            "fileId": file_id,
            "filename": original,
            "module": module,
            "mimeType": detected,
            "size": size,
            "sha256": sha.hexdigest(),
            "status": "uploaded"
        }
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)

@app.get("/api/files/{file_id}")
def download_file(file_id: str, authorization: str | None = Header(default=None)):
    user = require_user(authorization)
    db = SessionLocal()
    try:
        record = db.get(FileRecord, file_id)
        if not record:
            raise HTTPException(404, "Ficheiro não encontrado")
        # TODO: substituir por autorização clínica real baseada em paciente/perfil.
        path = STORAGE_DIR / record.stored_name
        if not path.exists():
            raise HTTPException(404, "Ficheiro físico não encontrado")
        return FileResponse(
            path,
            media_type=record.mime_type,
            filename=record.original_name,
            headers={"X-Content-Type-Options":"nosniff",
                     "Content-Disposition":f'attachment; filename="{record.original_name}"'}
        )
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status":"ok","service":"MEDTRAIL Upload API"}
