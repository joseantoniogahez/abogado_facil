from fastapi import APIRouter

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.setup.dependencies import AIInsightsServiceDependency
from app.features.ai_insights.openapi import FEEDBACK_DOC, INSIGHTS_DOC
from app.features.ai_insights.schemas import (
    AIInsightsResponse,
    AIResultFeedbackRequest,
    AIResultFeedbackResponse,
)

router = APIRouter(prefix="/ai/insights", tags=["ai-insights"])


def _firm_id(user: AuthenticatedReadAccessDependency) -> int:
    if user.firm_id is None:
        raise ValueError("Authenticated AI users must belong to a firm")
    return user.firm_id


@router.get("", response_model=AIInsightsResponse, **INSIGHTS_DOC)
async def get_insights(user: AuthenticatedReadAccessDependency, service: AIInsightsServiceDependency):
    return await service.get_insights(firm_id=_firm_id(user))


@router.put("/results/{result_id}/feedback", response_model=AIResultFeedbackResponse, **FEEDBACK_DOC)
async def save_feedback(
    result_id: int,
    payload: AIResultFeedbackRequest,
    user: AuthenticatedReadAccessDependency,
    service: AIInsightsServiceDependency,
):
    return await service.save_feedback(
        result_id=result_id, user_id=user.id, firm_id=_firm_id(user), category=payload.category
    )
