from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# ==================== AUTH ====================
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    organization_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: UUID
    email: str
    role: str
    
    class Config:
        from_attributes = True

# ==================== ORGANIZATION ====================
class OrganizationCreate(BaseModel):
    name: str
    email: EmailStr

class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    email: str
    
    class Config:
        from_attributes = True

# ==================== TENDER ====================
class TenderUploadResponse(BaseModel):
    tender_id: UUID
    job_id: str
    status: str
    message: str

class TenderStatusResponse(BaseModel):
    tender_id: UUID
    status: str
    page_count: Optional[int]
    processed_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

class TenderResponse(BaseModel):
    id: UUID
    file_name: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== ANALYSIS ====================
class TenderAnalysisResponse(BaseModel):
    tender_id: UUID
    summary: Optional[str]
    tender_value: Optional[float]
    bid_deadline: Optional[datetime]
    sector: Optional[str]
    location: Optional[str]
    eligibility_criteria: Dict[str, Any]
    required_documents: List[str]
    
    class Config:
        from_attributes = True

# ==================== SCORING ====================
class TenderScoreResponse(BaseModel):
    win_probability: float
    eligibility_score: float
    fit_score: float
    risk_level: str
    competition_intensity: str
    recommendation: str
    reasoning: List[str]
    
    class Config:
        from_attributes = True

class CompanyProfileCreate(BaseModel):
    company_name: str
    annual_turnover: float
    net_worth: float
    team_size: int
    sectors: List[str]
    operating_states: List[str]
    certifications: Dict[str, bool]
    registrations: Dict[str, str]
    years_in_business: int

class CompanyProfileResponse(BaseModel):
    id: UUID
    company_name: str
    annual_turnover: float
    team_size: int
    sectors: List[str]
    
    class Config:
        from_attributes = True

# ==================== Q&A ====================
class TenderQARequest(BaseModel):
    question: str
    top_k: int = 5

class TenderQAResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float

# ==================== JOB STATUS ====================
class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[float]
    result: Optional[Dict[str, Any]]
    error: Optional[str]

# ==================== USAGE ====================
class UsageResponse(BaseModel):
    tier: str
    tenders_analyzed: int
    tenders_limit: int
    percent_used: float

