import csv
from io import StringIO
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database.db import SessionLocal, engine
from database.models import Base, User, Asset, ServiceRequest, WorkOrder, PPMSchedule, Vendor

# Initialize App
app = FastAPI()

# Create Tables
Base.metadata.create_all(bind=engine)

# Setup Static Files and Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- AUTHENTICATION ROUTES ---

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return RedirectResponse(url="/dashboard")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_user(username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username, User.password == password).first()
    db.close()

    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return {"message": "Invalid Username or Password"}

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_user(username: str = Form(...), password: str = Form(...), role: str = Form(...)):
    db = SessionLocal()
    user = User(username=username, password=password, role=role, is_active="Active")
    db.add(user)
    db.commit()
    db.close()
    return RedirectResponse(url="/view-users", status_code=302)

# --- DASHBOARD ---

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    db = SessionLocal()
    try:
        asset_count = db.query(Asset).count()
        user_count = db.query(User).count()
        request_count = db.query(ServiceRequest).count()
        workorder_count = db.query(WorkOrder).count()
        ppm_count = db.query(PPMSchedule).count()
        vendor_count = db.query(Vendor).count()
    except Exception:
        asset_count = user_count = request_count = workorder_count = ppm_count = vendor_count = 0
    finally:
        db.close()

    return templates.TemplateResponse(
    request=request,
    name="dashboard.html",
    context={
        "asset_count": asset_count,
        "user_count": user_count,
        "request_count": request_count,
        "workorder_count": workorder_count,
        "ppm_count": ppm_count,
        "vendor_count": vendor_count
    }
    )

# --- ASSET MANAGEMENT ---

@app.get("/assets", response_class=HTMLResponse)
def assets_page(request: Request):
    return templates.TemplateResponse("assets.html", {"request": request})

@app.post("/assets")
def add_asset(asset_code: str = Form(...), asset_name: str = Form(...), location: str = Form(...), status: str = Form(...)):
    db = SessionLocal()
    asset = Asset(asset_code=asset_code, asset_name=asset_name, location=location, status=status)
    db.add(asset)
    db.commit()
    db.close()
    return {"message": "Asset Added Successfully"}

@app.get("/view-assets", response_class=HTMLResponse)
def view_assets(request: Request):
    db = SessionLocal()
    assets = db.query(Asset).all()
    db.close()
    return templates.TemplateResponse("view_assets.html", {"request": request, "assets": assets})

@app.get("/edit-asset/{asset_id}", response_class=HTMLResponse)
def edit_asset_page(asset_id: int, request: Request):
    db = SessionLocal()
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    db.close()
    return templates.TemplateResponse("edit_asset.html", {"request": request, "asset": asset})

@app.post("/edit-asset/{asset_id}")
def update_asset(asset_id: int, asset_code: str = Form(...), asset_name: str = Form(...), location: str = Form(...), status: str = Form(...)):
    db = SessionLocal()
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    asset.asset_code = asset_code
    asset.asset_name = asset_name
    asset.location = location
    asset.status = status
    db.commit()
    db.close()
    return RedirectResponse(url="/view-assets", status_code=302)

@app.get("/delete-asset/{asset_id}")
def delete_asset(asset_id: int):
    db = SessionLocal()
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if asset:
        db.delete(asset)
        db.commit()
    db.close()
    return RedirectResponse(url="/view-assets", status_code=302)

# --- SERVICE REQUESTS ---

@app.get("/requests", response_class=HTMLResponse)
def requests_page(request: Request):
    return templates.TemplateResponse("requests.html", {"request": request})

@app.post("/requests")
def create_request(title: str = Form(...), description: str = Form(...), priority: str = Form(...)):
    db = SessionLocal()
    request_obj = ServiceRequest(
        title=title, description=description, priority=priority,
        status="Open", assigned_to="", remarks="", created_by="Admin"
    )
    db.add(request_obj)
    db.commit()
    db.close()
    return RedirectResponse(url="/view-requests", status_code=302)

@app.get("/view-requests", response_class=HTMLResponse)
def view_requests(request: Request):
    db = SessionLocal()
    requests = db.query(ServiceRequest).all()
    db.close()
    return templates.TemplateResponse("view_requests.html", {"request": request, "requests": requests})

@app.get("/edit-request/{request_id}", response_class=HTMLResponse)
def edit_request_page(request_id: int, request: Request):
    db = SessionLocal()
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    db.close()
    return templates.TemplateResponse("edit_request.html", {"request": request, "req": req})

@app.post("/edit-request/{request_id}")
def update_request(request_id: int, status: str = Form(...), assigned_to: str = Form(...), remarks: str = Form(...)):
    db = SessionLocal()
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    req.status = status
    req.assigned_to = assigned_to
    req.remarks = remarks
    db.commit()
    db.close()
    return RedirectResponse(url="/view-requests", status_code=302)

# --- WORK ORDERS ---

@app.get("/workorders", response_class=HTMLResponse)
def workorders_page(request: Request):
    return templates.TemplateResponse("workorders.html", {"request": request})

@app.post("/workorders")
def create_workorder(request_id: int = Form(...), title: str = Form(...), technician: str = Form(...)):
    db = SessionLocal()
    workorder = WorkOrder(
        request_id=request_id, title=title, technician=technician,
        status="Open", remarks="", completion_date=""
    )
    db.add(workorder)
    db.commit()
    db.close()
    return RedirectResponse(url="/view-workorders", status_code=302)

@app.get("/view-workorders", response_class=HTMLResponse)
def view_workorders(request: Request):
    db = SessionLocal()
    workorders = db.query(WorkOrder).all()
    db.close()
    return templates.TemplateResponse("view_workorders.html", {"request": request, "workorders": workorders})

@app.get("/edit-workorder/{wo_id}", response_class=HTMLResponse)
def edit_workorder_page(wo_id: int, request: Request):
    db = SessionLocal()
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    db.close()
    return templates.TemplateResponse("edit_workorder.html", {"request": request, "wo": wo})

@app.post("/edit-workorder/{wo_id}")
def update_workorder(wo_id: int, status: str = Form(...), remarks: str = Form(...), completion_date: str = Form(...)):
    db = SessionLocal()
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    wo.status = status
    wo.remarks = remarks
    wo.completion_date = completion_date
    db.commit()
    db.close()
    return RedirectResponse(url="/view-workorders", status_code=302)

# --- PPM SCHEDULE ---

@app.get("/ppm", response_class=HTMLResponse)
def ppm_page(request: Request):
    return templates.TemplateResponse("ppm.html", {"request": request})

@app.post("/ppm")
def create_ppm(asset_id: int = Form(...), asset_name: str = Form(...), frequency: str = Form(...), last_ppm_date: str = Form(...), next_due_date: str = Form(...), technician: str = Form(...)):
    db = SessionLocal()
    ppm = PPMSchedule(
        asset_id=asset_id, asset_name=asset_name, frequency=frequency,
        last_ppm_date=last_ppm_date, next_due_date=next_due_date,
        technician=technician, status="Upcoming", remarks=""
    )
    db.add(ppm)
    db.commit()
    db.close()
    return RedirectResponse(url="/view-ppm", status_code=302)

@app.get("/view-ppm", response_class=HTMLResponse)
def view_ppm(request: Request):
    db = SessionLocal()
    ppms = db.query(PPMSchedule).all()
    db.close()
    return templates.TemplateResponse("view_ppm.html", {"request": request, "ppms": ppms})

@app.get("/edit-ppm/{ppm_id}", response_class=HTMLResponse)
def edit_ppm_page(ppm_id: int, request: Request):
    db = SessionLocal()
    ppm = db.query(PPMSchedule).filter(PPMSchedule.id == ppm_id).first()
    db.close()
    return templates.TemplateResponse("edit_ppm.html", {"request": request, "ppm": ppm})

@app.post("/edit-ppm/{ppm_id}")
def update_ppm(ppm_id: int, status: str = Form(...), remarks: str = Form(...)):
    db = SessionLocal()
    ppm = db.query(PPMSchedule).filter(PPMSchedule.id == ppm_id).first()
    ppm.status = status
    ppm.remarks = remarks
    db.commit()
    db.close()
    return RedirectResponse(url="/view-ppm", status_code=302)

# --- VENDORS ---

@app.get("/vendors", response_class=HTMLResponse)
def vendors_page(request: Request):
    return templates.TemplateResponse("vendors.html", {"request": request})

@app.post("/vendors")
def create_vendor(vendor_code: str = Form(...), vendor_name: str = Form(...), category: str = Form(...), contact_person: str = Form(...), phone: str = Form(...), email: str = Form(...), amc_start: str = Form(...), amc_end: str = Form(...), status: str = Form(...)):
    db = SessionLocal()
    vendor = Vendor(vendor_code=vendor_code, vendor_name=vendor_name, category=category, contact_person=contact_person, phone=phone, email=email, amc_start=amc_start, amc_end=amc_end, status=status)
    db.add(vendor)
    db.commit()
    db.close()
    return RedirectResponse(url="/view-vendors", status_code=302)

@app.get("/view-vendors", response_class=HTMLResponse)
def view_vendors(request: Request):
    db = SessionLocal()
    vendors = db.query(Vendor).all()
    db.close()
    return templates.TemplateResponse("view_vendors.html", {"request": request, "vendors": vendors})

# --- REPORTS & USERS ---

@app.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request):
    db = SessionLocal()
    try:
        context = {
            "request": request,
            "asset_count": db.query(Asset).count(),
            "request_count": db.query(ServiceRequest).count(),
            "workorder_count": db.query(WorkOrder).count(),
            "ppm_count": db.query(PPMSchedule).count(),
            "vendor_count": db.query(Vendor).count(),
            "user_count": db.query(User).count()
        }
    except:
        context = {"request": request, "asset_count": 0, "request_count": 0, "workorder_count": 0, "ppm_count": 0, "vendor_count": 0, "user_count": 0}
    finally:
        db.close()
    return templates.TemplateResponse("reports.html", context)

@app.get("/view-users", response_class=HTMLResponse)
def view_users(request: Request):
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return templates.TemplateResponse("view_users.html", {"request": request, "users": users})

@app.get("/asset-report", response_class=HTMLResponse)
def asset_report(request: Request):
    db = SessionLocal()
    try:
        assets = db.query(Asset).all()
        return templates.TemplateResponse("asset_report.html", {"request": request, "assets": assets})
    finally:
        db.close()

@app.get("/export-assets")
def export_assets():
    db = SessionLocal()
    assets = db.query(Asset).all()
    db.close()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Code", "Name", "Location", "Status"])
    for asset in assets:
        writer.writerow([asset.asset_code, asset.asset_name, asset.location, asset.status])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=assets.csv"})

@app.get("/request-report", response_class=HTMLResponse)
def request_report(request: Request):
    db = SessionLocal()
    try:
        requests = db.query(ServiceRequest).all()
        return templates.TemplateResponse("request_report.html", {"request": request, "requests": requests})
    finally:
        db.close()

@app.get("/workorder-report", response_class=HTMLResponse)
def workorder_report(request: Request):
    db = SessionLocal()
    try:
        workorders = db.query(WorkOrder).all()
        return templates.TemplateResponse("workorder_report.html", {"request": request, "workorders": workorders})
    finally:
        db.close()

@app.get("/vendor-report", response_class=HTMLResponse)
def vendor_report(request: Request):
    db = SessionLocal()
    try:
        vendors = db.query(Vendor).all()
        return templates.TemplateResponse("vendor_report.html", {"request": request, "vendors": vendors})
    finally:
        db.close()

@app.get("/ppm-report", response_class=HTMLResponse)
def ppm_report(request: Request):
    db = SessionLocal()
    try:
        ppms = db.query(PPMSchedule).all()
        return templates.TemplateResponse("ppm_report.html", {"request": request, "ppms": ppms})
    finally:
        db.close()

@app.get("/user-report", response_class=HTMLResponse)
def user_report(request: Request):
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return templates.TemplateResponse("user_report.html", {"request": request, "users": users})
    finally:
        db.close()
    
