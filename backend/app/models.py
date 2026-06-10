from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Enum, ForeignKey, JSON, Text, Date, LargeBinary, Table, Numeric
from sqlalchemy.orm import relationship
from app.db_types import GUID as UUID, JSONB, ARRAY
from app.database import Base
import uuid
from datetime import datetime
import enum as py_enum

# ==================== ORGANIZATIONS ====================
class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    domain = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    max_monthly_analyses = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    subscriptions = relationship("Subscription", back_populates="organization")
    tenders = relationship("Tender", back_populates="organization")
    company_profiles = relationship("CompanyProfile", back_populates="organization")
    usage_logs = relationship("UsageLog", back_populates="organization")
    tender_scores = relationship("TenderScore", back_populates="organization")

# ==================== USERS ====================
class UserRole(str, py_enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.MEMBER)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")

# ==================== SUBSCRIPTIONS ====================
class SubscriptionTier(str, py_enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, py_enum.Enum):
    ACTIVE = "active"
    PAYMENT_FAILED = "payment_failed"
    HALTED = "halted"
    CANCELED = "canceled"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    razorpay_subscription_id = Column(String(255), nullable=True)
    razorpay_customer_id = Column(String(255), nullable=True)
    tier = Column(String(50), default=SubscriptionTier.FREE)
    status = Column(String(50), default=SubscriptionStatus.ACTIVE)
    price_per_month = Column(Numeric(10, 2), default=0)
    current_cycle_start = Column(DateTime, default=datetime.utcnow)
    current_cycle_end = Column(DateTime, nullable=True)
    next_billing_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="subscriptions")

# ==================== TENDERS ====================
class TenderStatus(str, py_enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Tender(Base):
    __tablename__ = "tenders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    company_profile_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id"), nullable=True)
    file_name = Column(String(255), nullable=False)
    s3_key = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(255), nullable=True)
    page_count = Column(Integer, nullable=True)
    is_scanned = Column(Boolean, default=False)
    status = Column(String(50), default=TenderStatus.PENDING)
    job_id = Column(String(255), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="tenders")
    analysis = relationship("TenderAnalysis", back_populates="tender", uselist=False)
    scores = relationship("TenderScore", back_populates="tender")

# ==================== TENDER ANALYSIS ====================
class TenderAnalysis(Base):
    __tablename__ = "tender_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    summary = Column(Text, nullable=True)
    tender_value = Column(Numeric(15, 2), nullable=True)
    bid_deadline = Column(DateTime, nullable=True)
    sector = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    eligibility_criteria = Column(JSONB, default={})
    required_documents = Column(JSONB, default={})
    penalty_clauses = Column(JSONB, default={})
    key_dates = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tender = relationship("Tender", back_populates="analysis")

# ==================== TENDER SCORES ====================
class TenderScore(Base):
    __tablename__ = "tender_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id"), nullable=False)
    company_profile_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    win_probability = Column(Float, default=0.0)
    eligibility_score = Column(Float, default=0.0)
    fit_score = Column(Float, default=0.0)
    risk_level = Column(String(50), default="medium")
    risk_score = Column(Float, default=0.0)
    competition_intensity = Column(String(50), default="medium")
    recommendation = Column(String(50), default="skip")
    factors = Column(JSONB, default={})
    reasoning = Column(JSONB, default=[])
    user_feedback = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tender = relationship("Tender", back_populates="scores")
    company_profile = relationship("CompanyProfile", back_populates="tender_scores")
    organization = relationship("Organization", back_populates="tender_scores")

# ==================== COMPANY PROFILES ====================
class CompanyProfile(Base):
    __tablename__ = "company_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    company_name = Column(String(255), nullable=False)
    annual_turnover = Column(Numeric(12, 2), nullable=True)
    net_worth = Column(Numeric(12, 2), nullable=True)
    team_size = Column(Integer, default=0)
    sectors = Column(ARRAY(String), default=[])
    operating_states = Column(ARRAY(String), default=[])
    certifications = Column(JSONB, default={})
    registrations = Column(JSONB, default={})
    years_in_business = Column(Integer, default=0)
    past_projects = Column(JSONB, default=[])
    bid_success_rate = Column(Float, default=0.5)
    liquid_assets = Column(Numeric(12, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="company_profiles")
    tender_scores = relationship("TenderScore", back_populates="company_profile")

# ==================== USAGE LOGS ====================
class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    month = Column(Date, nullable=False)
    tenders_analyzed = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    storage_used_mb = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="usage_logs")

# ==================== API LOGS ====================
class ApiLog(Base):
    __tablename__ = "api_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

