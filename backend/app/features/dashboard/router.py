from fastapi import APIRouter

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.setup.dependencies import AuthServiceDependency, DashboardServiceDependency
from app.features.dashboard.openapi import GET_DASHBOARD_DOC
from app.features.dashboard.schemas.api import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardSummaryResponse, **GET_DASHBOARD_DOC)
async def get_dashboard_summary(
    current_user: AuthenticatedReadAccessDependency,
    auth_service: AuthServiceDependency,
    dashboard_service: DashboardServiceDependency,
) -> DashboardSummaryResponse:
    profile = await auth_service.get_authenticated_user(current_user)
    if current_user.firm_id is None:
        raise ValueError("Authenticated dashboard users must belong to a firm")
    return await dashboard_service.get_summary(firm_id=current_user.firm_id, firm_name=profile.firm_name)
