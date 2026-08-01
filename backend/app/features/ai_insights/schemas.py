from datetime import datetime
from typing import Literal

from pydantic import ConfigDict

from app.core.common.schema import ApiSchema

FeedbackCategory = Literal["useful", "needs_correction", "fabricated", "missing_information"]


class AIResultFeedbackRequest(ApiSchema):
    category: FeedbackCategory


class AIResultFeedbackResponse(ApiSchema):
    result_id: int
    category: FeedbackCategory
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CountByName(ApiSchema):
    name: str
    count: int


class AIOperationalMetrics(ApiSchema):
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    success_rate: float
    average_latency_ms: float
    estimated_input_tokens: int
    estimated_output_tokens: int
    cost_usd: float | None
    cost_coverage_percent: float
    retry_count: int
    stuck_jobs: int
    errors: list[CountByName]


class AIProductMetrics(ApiSchema):
    total_results: int
    accepted_results: int
    partially_accepted_results: int
    rejected_results: int
    pending_results: int
    edited_results: int
    converted_results: int
    regenerated_results: int
    abandoned_results: int
    feedback: list[CountByName]


class AIInsightsResponse(ApiSchema):
    generated_at: datetime
    stuck_after_minutes: int
    operational: AIOperationalMetrics
    product: AIProductMetrics
