from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# -------------------------
# ASSET MANAGEMENT
# -------------------------

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String)
    asset_name = Column(String)
    location = Column(String)
    status = Column(String)


# -------------------------
# SERVICE REQUESTS
# -------------------------

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    status = Column(String)
    assigned_to = Column(String)
    remarks = Column(String)
    created_by = Column(String)


# -------------------------
# WORK ORDERS
# -------------------------

class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer)
    title = Column(String)
    technician = Column(String)
    status = Column(String)
    remarks = Column(String)
    completion_date = Column(String)


# -------------------------
# PPM SCHEDULE
# -------------------------

class PPMSchedule(Base):
    __tablename__ = "ppm_schedules"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer)
    asset_name = Column(String)
    frequency = Column(String)
    last_ppm_date = Column(String)
    next_due_date = Column(String)
    technician = Column(String)
    status = Column(String)
    remarks = Column(String)


# -------------------------
# VENDOR MANAGEMENT
# -------------------------

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    vendor_code = Column(String)
    vendor_name = Column(String)
    category = Column(String)
    contact_person = Column(String)
    phone = Column(String)
    email = Column(String)
    amc_start = Column(String)
    amc_end = Column(String)
    status = Column(String)


# -------------------------
# USER MANAGEMENT
# -------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)

    password = Column(String, nullable=False)

    role = Column(String)
    otp = Column(String)

    is_verified = Column(String, default="No")
    is_active = Column(String, default="Yes")


# -------------------------
# ACTIVITY LOGS
# -------------------------

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    action = Column(String)
    module = Column(String)
    created_at = Column(String)
