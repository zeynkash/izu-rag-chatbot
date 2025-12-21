"""
Structured Data Models for IZU University Content
Defines dataclasses for different types of university information
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import json


class ContentCategory(Enum):
    """Categories for university content"""
    ACADEMIC_PROGRAM = "academic_program"
    FACULTY_MEMBER = "faculty_member"
    ADMISSION = "admission"
    FEE_STRUCTURE = "fee_structure"
    EVENT = "event"
    NEWS = "news"
    RESEARCH = "research"
    STUDENT_SERVICE = "student_service"
    DEPARTMENT = "department"
    GENERAL = "general"


class DegreeType(Enum):
    """Academic degree types"""
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    CERTIFICATE = "certificate"
    DIPLOMA = "diploma"


class Language(Enum):
    """Teaching languages"""
    TURKISH = "turkish"
    ENGLISH = "english"
    BILINGUAL = "bilingual"


@dataclass
class AcademicProgram:
    """Academic program information"""
    program_name: str
    program_name_en: Optional[str] = None
    degree_type: Optional[str] = None
    faculty: Optional[str] = None
    department: Optional[str] = None
    duration_years: Optional[float] = None
    teaching_language: Optional[str] = None
    tuition_fee: Optional[str] = None
    description: Optional[str] = None
    admission_requirements: List[str] = field(default_factory=list)
    curriculum: List[str] = field(default_factory=list)
    career_opportunities: List[str] = field(default_factory=list)
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FacultyMember:
    """Faculty member profile"""
    name: str
    title: Optional[str] = None
    department: Optional[str] = None
    faculty: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    office: Optional[str] = None
    research_areas: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    publications: List[str] = field(default_factory=list)
    courses: List[str] = field(default_factory=list)
    bio: Optional[str] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AdmissionInfo:
    """Admission and application information"""
    program: Optional[str] = None
    degree_type: Optional[str] = None
    requirements: List[str] = field(default_factory=list)
    required_documents: List[str] = field(default_factory=list)
    application_deadline: Optional[str] = None
    application_process: List[str] = field(default_factory=list)
    entrance_exams: List[str] = field(default_factory=list)
    minimum_scores: Dict[str, str] = field(default_factory=dict)
    international_students: Optional[str] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FeeStructure:
    """Tuition fees and costs"""
    program: Optional[str] = None
    degree_type: Optional[str] = None
    academic_year: Optional[str] = None
    tuition_fee: Optional[str] = None
    tuition_fee_usd: Optional[str] = None
    registration_fee: Optional[str] = None
    other_fees: Dict[str, str] = field(default_factory=dict)
    scholarship_available: Optional[bool] = None
    scholarship_details: List[str] = field(default_factory=list)
    payment_options: List[str] = field(default_factory=list)
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Event:
    """University event or activity"""
    title: str
    title_en: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    organizer: Optional[str] = None
    registration_required: Optional[bool] = None
    registration_url: Optional[str] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NewsItem:
    """News article or announcement"""
    title: str
    title_en: Optional[str] = None
    date: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Department:
    """Department information"""
    name: str
    name_en: Optional[str] = None
    faculty: Optional[str] = None
    description: Optional[str] = None
    head: Optional[str] = None
    programs: List[str] = field(default_factory=list)
    research_areas: List[str] = field(default_factory=list)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchInfo:
    """Research centers and projects"""
    title: str
    title_en: Optional[str] = None
    research_center: Optional[str] = None
    description: Optional[str] = None
    research_areas: List[str] = field(default_factory=list)
    team_members: List[str] = field(default_factory=list)
    publications: List[str] = field(default_factory=list)
    funding: Optional[str] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StudentService:
    """Student services and facilities"""
    service_name: str
    service_name_en: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    contact_info: Optional[str] = None
    hours: Optional[str] = None
    online_service: Optional[bool] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PageData:
    """Generic page data with metadata"""
    url: str
    title: str
    category: str
    content: str
    language: str = "unknown"
    word_count: int = 0
    tables: List[List[List[str]]] = field(default_factory=list)
    lists: List[List[str]] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)
    documents: List[Dict[str, str]] = field(default_factory=list)
    contact_info: Dict[str, List[str]] = field(default_factory=dict)
    breadcrumb: List[str] = field(default_factory=list)
    meta_description: Optional[str] = None
    date_scraped: Optional[str] = None
    content_hash: Optional[str] = None
    
    # Structured data (if applicable)
    structured_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


def create_structured_data(category: ContentCategory, data: Dict[str, Any]) -> Optional[Any]:
    """
    Create appropriate structured data object based on category
    
    Args:
        category: Content category
        data: Dictionary with extracted data
        
    Returns:
        Structured data object or None
    """
    try:
        if category == ContentCategory.ACADEMIC_PROGRAM:
            return AcademicProgram(**data)
        elif category == ContentCategory.FACULTY_MEMBER:
            return FacultyMember(**data)
        elif category == ContentCategory.ADMISSION:
            return AdmissionInfo(**data)
        elif category == ContentCategory.FEE_STRUCTURE:
            return FeeStructure(**data)
        elif category == ContentCategory.EVENT:
            return Event(**data)
        elif category == ContentCategory.NEWS:
            return NewsItem(**data)
        elif category == ContentCategory.DEPARTMENT:
            return Department(**data)
        elif category == ContentCategory.RESEARCH:
            return ResearchInfo(**data)
        elif category == ContentCategory.STUDENT_SERVICE:
            return StudentService(**data)
    except Exception as e:
        print(f"Error creating structured data for {category}: {e}")
        return None
    
    return None
