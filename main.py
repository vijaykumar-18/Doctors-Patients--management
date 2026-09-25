# ============================================================
# DOCTOR-PATIENT MANAGEMENT SYSTEM
# FastAPI + SQLAlchemy + SQLite + JWT Authentication
# ============================================================

# ============================================================
# IMPORTS
# ============================================================

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from dotenv import load_dotenv

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Query,
    status
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator
)

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    create_engine
)

from sqlalchemy.orm import (
    Session,
    declarative_base,
    relationship,
    sessionmaker
)

from pwdlib import PasswordHash


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./assignment2.db"
)

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key"
)

ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30"
    )
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    """
    Create a database session for each request.
    Close the session after the request finishes.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# DOCTOR-PATIENT ASSOCIATION TABLE
# ============================================================


doctor_patient_table = Table(
    "doctor_patient",

    Base.metadata,

    Column(
        "doctor_id",
        Integer,
        ForeignKey("doctors.id"),
        primary_key=True
    ),

    Column(
        "patient_id",
        Integer,
        ForeignKey("patients.id"),
        primary_key=True
    )
)


# ============================================================
# USER MODEL
# ============================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

 
    role = Column(
        String(20),
        nullable=False,
        default="doctor"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )


# ============================================================
# DOCTOR MODEL
# ============================================================

class Doctor(Base):

    __tablename__ = "doctors"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    name = Column(
        String(100),
        nullable=False
    )

    specialization = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )


    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    user = relationship(
        "User"
    )

    patients = relationship(
        "Patient",
        secondary=doctor_patient_table,
        back_populates="doctors"
    )


# ============================================================
# PATIENT MODEL
# ============================================================

class Patient(Base):

    __tablename__ = "patients"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    age = Column(
        Integer,
        nullable=False
    )

    phone = Column(
        String(15),
        nullable=False
    )

    doctors = relationship(
        "Doctor",
        secondary=doctor_patient_table,
        back_populates="patients"
    )


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# PASSWORD HASHING
# ============================================================

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Convert plain password into a secure hash.
    """

    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    """
    Verify a plain password against a stored hash.
    """

    return password_hash.verify(
        password,
        hashed_password
    )


# ============================================================
# JWT AUTHENTICATION
# ============================================================

security = HTTPBearer()


def create_access_token(
    user_id: int,
    role: str
) -> str:
    """
    Create a JWT access token.
    """

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# ============================================================
# GET CURRENT USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db)
):
    """
    Read JWT token and find the logged-in user.
    """

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user_id = int(user_id)

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )

    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


# ============================================================
# ADMIN AUTHORIZATION
# ============================================================

def require_admin(
    current_user: User = Depends(
        get_current_user
    )
):
    """
    Allow only Admin users.
    """

    if current_user.role != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user


# ============================================================
# DOCTOR OR ADMIN AUTHORIZATION
# ============================================================

def require_doctor_or_admin(
    current_user: User = Depends(
        get_current_user
    )
):
    """
    Allow Admin and Doctor users.
    """

    if current_user.role not in {
        "admin",
        "doctor"
    }:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor or Admin access required"
        )

    return current_user


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================


# ============================================================
# REGISTER SCHEMA
# ============================================================

class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100
    )


# ============================================================
# LOGIN SCHEMA
# ============================================================

class LoginRequest(BaseModel):

    email: EmailStr

    password: str


# ============================================================
# TOKEN RESPONSE
# ============================================================

class TokenResponse(BaseModel):

    access_token: str

    token_type: str


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):

    id: int

    name: str

    email: EmailStr

    role: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# DOCTOR CREATE SCHEMA
# ============================================================

class DoctorCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    specialization: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100
    )


# ============================================================
# DOCTOR UPDATE SCHEMA
# ============================================================

class DoctorUpdate(BaseModel):

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    specialization: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: Optional[EmailStr] = None


# ============================================================
# DOCTOR RESPONSE
# ============================================================

class DoctorResponse(BaseModel):

    id: int

    name: str

    specialization: str

    email: EmailStr

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# PATIENT CREATE SCHEMA
# ============================================================

class PatientCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    age: int = Field(
        gt=0
    )

    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str):

        if not value.isdigit():

            raise ValueError(
                "Phone number must contain only digits"
            )

        if not 10 <= len(value) <= 15:

            raise ValueError(
                "Phone number must contain 10-15 digits"
            )

        return value


# ============================================================
# PATIENT RESPONSE
# ============================================================

class PatientResponse(BaseModel):

    id: int

    name: str

    age: int

    phone: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Doctor-Patient Management API",

    description="""
    Backend system for managing Doctors and Patients.

    Features:
    - JWT Authentication
    - Role-based Authorization
    - Doctor Management
    - Patient Management
    - Doctor-Patient Assignment
    - Soft Delete
    - Validation
    - Pagination
    - Doctor specialization filtering
    """,

    version="1.0.0"
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get(
    "/",
    tags=["Health Check"]
)
def root():

    return {
        "message": "Doctor-Patient Management API is running",
        "docs": "/docs"
    }


# ============================================================
# AUTHENTICATION
# ============================================================


# ============================================================
# REGISTER
# ============================================================

@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"]
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new Doctor user.

    IMPORTANT:
    Public registration cannot create an Admin.
    New users are always created as Doctors.
    """

    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(
            request.password
        ),
        role="doctor",
        is_active=True
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


# ============================================================
# LOGIN
# ============================================================

@app.post(
    "/auth/login",
    response_model=TokenResponse,
    tags=["Authentication"]
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login using email and password.
    """

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(
        request.password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    token = create_access_token(
        user.id,
        user.role
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ============================================================
# DOCTOR MANAGEMENT
# ============================================================


# ============================================================
# CREATE DOCTOR
# ============================================================

@app.post(
    "/doctors",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Doctors"]
)
def create_doctor(
    request: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a Doctor.

    Admin only.
    """

    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_doctor = db.query(Doctor).filter(
        Doctor.email == request.email
    ).first()

    if existing_doctor:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor email already exists"
        )

    user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(
            request.password
        ),
        role="doctor",
        is_active=True
    )

    db.add(user)

    db.flush()

    doctor = Doctor(
        user_id=user.id,
        name=request.name,
        specialization=request.specialization,
        email=request.email,
        is_active=True
    )

    db.add(doctor)

    db.commit()

    db.refresh(doctor)

    return doctor


# ============================================================
# LIST DOCTORS
# ============================================================

@app.get(
    "/doctors",
    response_model=list[DoctorResponse],
    tags=["Doctors"]
)
def list_doctors(
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip"
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum records to return"
    ),

    specialization: Optional[str] = Query(
        default=None,
        description="Filter by specialization"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):
    """
    List active doctors.

    Supports:
    - Pagination
    - Specialization filtering
    """

    query = db.query(Doctor).filter(
        Doctor.is_active == True
    )

    if specialization:

        query = query.filter(
            Doctor.specialization.ilike(
                f"%{specialization}%"
            )
        )

    doctors = query.offset(
        skip
    ).limit(
        limit
    ).all()

    return doctors


# ============================================================
# GET DOCTOR
# ============================================================

@app.get(
    "/doctors/{doctor_id}",
    response_model=DoctorResponse,
    tags=["Doctors"]
)
def get_doctor(
    doctor_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):
    """
    Get one active doctor.
    """

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active == True
    ).first()

    if not doctor:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    return doctor


# ============================================================
# UPDATE DOCTOR
# ============================================================

@app.put(
    "/doctors/{doctor_id}",
    response_model=DoctorResponse,
    tags=["Doctors"]
)
def update_doctor(
    doctor_id: int,

    request: DoctorUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_admin
    )
):
    """
    Update doctor.

    Admin only.
    """

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active == True
    ).first()

    if not doctor:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )


    if request.email:

        existing_doctor = db.query(Doctor).filter(
            Doctor.email == request.email,
            Doctor.id != doctor_id
        ).first()

        if existing_doctor:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor email already exists"
            )

        existing_user = db.query(User).filter(
            User.email == request.email,
            User.id != doctor.user_id
        ).first()

        if existing_user:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        doctor.email = request.email

        doctor.user.email = request.email

    if request.name:

        doctor.name = request.name

        doctor.user.name = request.name


    if request.specialization:

        doctor.specialization = (
            request.specialization
        )

    db.commit()

    db.refresh(doctor)

    return doctor


# ============================================================
# DELETE DOCTOR
# ============================================================

@app.delete(
    "/doctors/{doctor_id}",
    tags=["Doctors"]
)
def delete_doctor(
    doctor_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_admin
    )
):
    """
    Soft delete doctor.

    The database row is NOT deleted.
    is_active is changed to False.
    """

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active == True
    ).first()

    if not doctor:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    doctor.is_active = False

    doctor.user.is_active = False

    db.commit()

    return {
        "message": "Doctor deleted successfully"
    }


# ============================================================
# PATIENT MANAGEMENT
# ============================================================


# ============================================================
# CREATE PATIENT
# ============================================================

@app.post(
    "/patients",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Patients"]
)
def create_patient(
    request: PatientCreate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_admin
    )
):
    """
    Create patient.

    Admin only.
    """

    patient = Patient(
        name=request.name,
        age=request.age,
        phone=request.phone
    )

    db.add(patient)

    db.commit()

    db.refresh(patient)

    return patient


# ============================================================
# LIST PATIENTS
# ============================================================

@app.get(
    "/patients",
    response_model=list[PatientResponse],
    tags=["Patients"]
)
def list_patients(
    skip: int = Query(
        default=0,
        ge=0
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_doctor_or_admin
    )
):
    """
    Admin:
        Can see all patients.

    Doctor:
        Can see only assigned patients.
    """

    if current_user.role == "admin":

        return db.query(
            Patient
        ).offset(
            skip
        ).limit(
            limit
        ).all()

    doctor = db.query(Doctor).filter(
        Doctor.user_id == current_user.id,
        Doctor.is_active == True
    ).first()

    if not doctor:

        return []

    patients = doctor.patients

    return patients[
        skip:skip + limit
    ]


# ============================================================
# GET PATIENT
# ============================================================

@app.get(
    "/patients/{patient_id}",
    response_model=PatientResponse,
    tags=["Patients"]
)
def get_patient(
    patient_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_doctor_or_admin
    )
):
    """
    Get patient.

    Admin:
        Can see any patient.

    Doctor:
        Can see only assigned patients.
    """

    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    if current_user.role == "admin":

        return patient

    doctor = db.query(Doctor).filter(
        Doctor.user_id == current_user.id,
        Doctor.is_active == True
    ).first()

    if not doctor:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor profile not found"
        )

    if patient not in doctor.patients:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this patient"
        )

    return patient


# ============================================================
# DOCTOR-PATIENT ASSIGNMENT
# ============================================================


# ============================================================
# ASSIGN PATIENT TO DOCTOR
# ============================================================

@app.post(
    "/doctors/{doctor_id}/patients/{patient_id}",
    tags=["Doctor-Patient Assignment"]
)
def assign_patient(
    doctor_id: int,

    patient_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_admin
    )
):
    """
    Assign patient to doctor.

    Admin only.
    """

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active == True
    ).first()

    if not doctor:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    if patient in doctor.patients:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient is already assigned to this doctor"
        )

    doctor.patients.append(
        patient
    )

    db.commit()

    return {
        "message": "Patient assigned to doctor successfully"
    }


# ============================================================
# GET DOCTOR'S PATIENTS
# ============================================================

@app.get(
    "/doctors/{doctor_id}/patients",
    response_model=list[PatientResponse],
    tags=["Doctor-Patient Assignment"]
)
def get_doctor_patients(
    doctor_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_doctor_or_admin
    )
):
    """
    Get patients assigned to a doctor.

    Admin:
        Can view any doctor's patients.

    Doctor:
        Can view ONLY their own patients.
    """

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active == True
    ).first()

    if not doctor:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    if current_user.role == "admin":

        return doctor.patients

    if doctor.user_id != current_user.id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctors can only view their own patients"
        )

    return doctor.patients


# ============================================================
# END OF APPLICATION
# ============================================================
