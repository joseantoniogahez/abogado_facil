from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import NotFoundError
from app.features.ai_insights.repository import AIInsightsRepository


class AIInsightsService:
    def __init__(self, repository: AIInsightsRepository, unit_of_work: UnitOfWorkPort):
        self.repository = repository
        self.unit_of_work = unit_of_work

    async def get_insights(self, *, firm_id: int):
        return await self.repository.insights(firm_id=firm_id)

    async def save_feedback(self, *, result_id: int, user_id: int, firm_id: int, category: str):
        async with self.unit_of_work:
            feedback = await self.repository.upsert_feedback(
                result_id=result_id, user_id=user_id, firm_id=firm_id, category=category
            )
            if feedback is None:
                raise NotFoundError("AI result not found")
            return feedback
