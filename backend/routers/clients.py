# backend/routers/clients.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from core.database import get_db
from models.schema import Client

router = APIRouter(prefix="/api/clients", tags=["Clients"])   # ← 改成 /api/clients

class ClientCreate(BaseModel):
    name: str
    bark_url: str | None = None
    wechat_webhook: str | None = None
    expire_date: datetime

class ClientRead(BaseModel):
    id: int
    name: str
    bark_url: str | None
    wechat_webhook: str | None
    expire_date: datetime
    is_active: bool

@router.post("/", response_model=ClientRead)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("/", response_model=List[ClientRead])
def list_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Client).offset(skip).limit(limit).all()

@router.get("/{client_id}", response_model=ClientRead)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client