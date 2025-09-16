# backend/app/api/tools.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import uuid, math
from ..db.session import get_db
from ..db.models import CreatedTool, CreatedToolVersion

router = APIRouter(prefix="/api/v1/tools", tags=["tools"])

class ToolIn(BaseModel):
  name: str
  content: str = ""
  specs: dict | None = None
  valves: dict | None = None
  access_control: dict | None = None

class ToolOut(BaseModel):
  id: str
  name: str
  is_active: bool
  updated_at: int | None = None
  content: str | None = None

@router.get("", response_model=list[ToolOut])
def list_tools(db: Session = Depends(get_db)):
  q = db.query(CreatedTool).order_by(CreatedTool.updated_at.desc()).all()
  return [ToolOut(id=t.id, name=t.name, is_active=t.is_active, updated_at=t.updated_at, content=getattr(t, "content", None)) for t in q]

@router.post("", response_model=ToolOut)
def create_tool(payload: ToolIn, db: Session = Depends(get_db)):
  tool_id = str(uuid.uuid4())
  t = CreatedTool(
    id=tool_id, name=payload.name, specs=payload.specs, valves=payload.valves,
    content=payload.content, access_control=payload.access_control
  )
  db.add(t)
  # initial immutable version 1
  v = CreatedToolVersion(id=str(uuid.uuid4()), tool_id=tool_id, version=1, content=payload.content or "")
  db.add(v)
  db.commit()
  return ToolOut(id=tool_id, name=t.name, is_active=t.is_active, updated_at=t.updated_at, content=t.content)

class PublishIn(BaseModel):
  content: str

@router.post("/{tool_id}/versions")
def publish_version(tool_id: str, payload: PublishIn, db: Session = Depends(get_db)):
  tool = db.query(CreatedTool).filter(CreatedTool.id == tool_id).first()
  if not tool:
    raise HTTPException(404, "tool_not_found")
  # compute next version
  max_ver = db.query(CreatedToolVersion.version).filter(CreatedToolVersion.tool_id == tool_id).order_by(CreatedToolVersion.version.desc()).first()
  next_ver = (max_ver[0] if max_ver else 0) + 1
  v = CreatedToolVersion(id=str(uuid.uuid4()), tool_id=tool_id, version=next_ver, content=payload.content)
  tool.content = payload.content  # convenience: mirror latest
  db.add(v)
  db.add(tool)
  db.commit()
  return {"tool_id": tool_id, "version": next_ver}

class TestRunIn(BaseModel):
  code: str
  input: dict | None = None

@router.post("/test-run")
def test_run(payload: TestRunIn):
  # MVP: do not execute arbitrary code here. Return a stubbed response so UI works.
  # TODO: call sandbox service with time/memory/stdlib restrictions.
  return {
    "ok": True,
    "message": "Sandbox disabled in MVP. Code length received: %d chars" % len(payload.code or ""),
  }
