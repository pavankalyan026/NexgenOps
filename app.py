import csv
import os
from io import StringIO
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database.db import SessionLocal, engine
from database.models import Base, User, Asset, ServiceRequest, WorkOrder, PPMSchedule, Vendor

# Initialize App
app = FastAPI()

# Create Tables
Base.metadata.create_all(bind=engine)

# Setup Static Files and Templates
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- DATABASE DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- AUTHENTICATION ---

@app.post("/login")
def login_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return {"message": "Invalid Username or Password"}

@app.post("/register")
def register_user(username: str=Form(...), email: str=Form(...), password: str=Form(...), role: str=Form(...), db: Session = Depends(get_db)):
    user = User(username=username, email=email, password=password, role=role, is_active="Yes")
    db.add(user)
    db.commit()
    return RedirectResponse(url="/view-users", status_code=302)

# --- DASHBOARD ---

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    context = {
        "request": request,
        "asset_count": db.query(Asset).count(),
        "user_count": db.query(User).count(),
        "request_count": db.query(ServiceRequest).count(),
        "workorder_count": db.query(WorkOrder).count(),
        "ppm_count": db.query(PPMSchedule).count(),
        "vendor_count": db.query(Vendor).count()
    }
    return templates.TemplateResponse("dashboard.html", context)

# --- ASSET MANAGEMENT ---

@app.post("/assets")
def add_asset(asset_code: str=Form(...), asset_name: str=Form(...), location: str=Form(...), status: str=Form(...), db: Session = Depends(get_db)):
    asset = Asset(asset_code=asset_code, asset_name=asset_name, location=location, status=status)
    db.add(asset)
    db.commit()
    return RedirectResponse(url="/view-assets", status_code=302)

@app.post("/edit-asset/{asset_id}")
def update_asset(asset_id: int, asset_code: str=Form(...), asset_name: str=Form(...), location: str=Form(...), status: str=Form(...), db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if asset:
        asset.asset_code, asset.asset_name, asset.location, asset.status = asset_code, asset_name, location, status
        db.commit()
    return RedirectResponse(url="/view-assets", status_code=302)

# --- WORK ORDERS & REQUESTS (Following the same pattern) ---

@app.post("/requests")
def create_request(title: str=Form(...), description: str=Form(...), priority: str=Form(...), db: Session = Depends(get_db)):
    req = ServiceRequest(title=title, description=description, priority=priority, status="Open", created_by="Admin")
    db.add(req)
    db.commit()
    return RedirectResponse(url="/view-requests", status_code=302)

@app.post("/edit-workorder/{wo_id}")
def update_workorder(wo_id: int, status: str=Form(...), remarks: str=Form(...), completion_date: str=Form(...), db: Session = Depends(get_db)):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if wo:
        wo.status, wo.remarks, wo.completion_date = status, remarks, completion_date
        db.commit()
    return RedirectResponse(url="/view-workorders", status_code=302)

# --- EXPORTS ---

@app.get("/export-assets")
def export_assets(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Code", "Name", "Location", "Status"])
    for a in assets:
        writer.writerow([a.asset_code, a.asset_name, a.location, a.status])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=assets.csv"})

# ... Repeat this pattern for all other POST and GET routes ...
