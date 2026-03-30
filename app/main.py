from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import time
import random

from .models import Event
from .database import SessionLocal, Base, engine
from fastapi import Query
from pydantic import BaseModel
from typing import Optional, Dict
import logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "dev")
SERVICE_NAME = os.getenv("SERVICE_NAME", "skynet-ops-audit-service")

REQUEST_COUNT = Counter("request_count", "Total API Requests",  ["method", "endpoint"])
ERROR_COUNT = Counter("error_count", "Total Errors",  ["method", "endpoint"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency")

Base.metadata.create_all(bind=engine)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

class EventCreate(BaseModel):
    type: str
    tenantId: str
    severity: str
    message: str
    source: str

    metadata: Optional[Dict] = None
    occurredAt: Optional[datetime] = None
    traceId: Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

VALID_SEVERITIES = ["info", "warning", "error", "critical"]

@app.post("/events", status_code=201)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    REQUEST_COUNT.labels(method="POST", endpoint="/events").inc()

    with REQUEST_LATENCY.time():
        try:

            # validation
            if not event.tenantId.strip():
                raise HTTPException(status_code=400, detail="tenantId required")

            if not event.message.strip():
                raise HTTPException(status_code=400, detail="message required")

            if event.severity not in VALID_SEVERITIES:
                raise HTTPException(status_code=400, detail="invalid severity")

            # generate id
            event_id = "evt_" + uuid.uuid4().hex[:14]
            stored_time = datetime.utcnow()

            # create object (MATCH YOUR MODEL EXACTLY)
            new_event = Event(
                eventId=event_id,
                type=event.type,
                tenantId=event.tenantId,
                severity=event.severity,
                message=event.message,
                source=event.source,
                metadata_=event.metadata,
                occurredAt=event.occurredAt or datetime.utcnow(),
                traceId=event.traceId,
                storedAt=stored_time
            )

            db.add(new_event)
            db.commit()

            logger.info(f"Event created: {event_id} | tenant: {event.tenantId} | severity: {event.severity}")

            return {
                "success": True,
                "eventId": event_id,
                "storedAt": stored_time.isoformat()
            }
        except Exception as e:
            ERROR_COUNT.labels(method="POST", endpoint="/events").inc()
            raise e

@app.get("/events")
def get_events(
    tenantId: str = None,
    severity: str = None,
    type: str = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    REQUEST_COUNT.labels(method="GET", endpoint="/events").inc() #check this

    with REQUEST_LATENCY.time():
        try:
    
            query = db.query(Event)
            if limit > 100:
                limit = 100

            # filters
            if tenantId:
                query = query.filter(Event.tenantId == tenantId)

            if severity:
                if severity not in VALID_SEVERITIES:
                    raise HTTPException(status_code=400, detail="invalid severity")
                query = query.filter(Event.severity == severity)

            if type:
                query = query.filter(Event.type == type)

            total = query.count()

            events = (
                query
                .order_by(Event.storedAt.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            items = []
            for e in events:
                items.append({
                    "eventId": e.eventId,
                    "type": e.type,
                    "tenantId": e.tenantId,
                    "severity": e.severity,
                    "message": e.message,
                    "source": e.source,
                    "metadata": e.metadata_,
                    "occurredAt": e.occurredAt.isoformat() if e.occurredAt else None,
                    "storedAt": e.storedAt.isoformat()
                })

            logger.info(f"Fetched {len(items)} events | tenant={tenantId} severity={severity}")

            return {
                "items": items,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            ERROR_COUNT.labels(method="GET", endpoint="/events").inc()
            raise e


@app.get("/health")
def health():

    REQUEST_COUNT.labels(method="GET", endpoint="/health").inc()

    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "environment": APP_ENV,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/metrics-demo")
def metrics_demo(mode: str = "success"):

    REQUEST_COUNT.labels(method="GET", endpoint="/metrics-demo").inc()

    with REQUEST_LATENCY.time():

        if mode == "error":
            ERROR_COUNT.labels(method="GET", endpoint="/metrics-demo").inc()
            logger.error("metrics-demo triggered error mode")
            raise HTTPException(status_code=500, detail="Simulated error")

        elif mode == "slow":
            logger.warning("metrics-demo slow mode — sleeping 2s")
            time.sleep(2)
            return {"mode": "slow", "message": "2s delay simulated"}

        elif mode == "burst":
            for i in range(5):
                logger.info(f"[BURST] log {i+1}/5 | tenant=demo")
            return {"mode": "burst", "message": "logs emitted"}

        else:
            logger.info("metrics-demo success mode")
            return {
                "mode": "success",
                "message": "OK",
                "available_modes": ["success", "error", "slow", "burst"]
            }