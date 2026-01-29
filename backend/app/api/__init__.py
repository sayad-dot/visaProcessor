"""
API Router - Main router for all API endpoints
"""
from fastapi import APIRouter

from app.api.endpoints import applications, documents, generate, required_documents, analysis, questionnaire

router = APIRouter()

# Include all endpoint routers
router.include_router(applications.router, prefix="/applications", tags=["Applications"])
router.include_router(documents.router, prefix="/documents", tags=["Documents"])
router.include_router(generate.router, prefix="/generate", tags=["Generate"])
router.include_router(required_documents.router, prefix="/required-documents", tags=["Required Documents"])
router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
router.include_router(questionnaire.router, prefix="/questionnaire", tags=["Questionnaire"])
