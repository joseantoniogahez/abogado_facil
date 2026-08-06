import json
from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.ai_assistance.models import AIAssistanceResult
from app.features.ai_insights.models import AIResultFeedback
from app.features.ai_insights.schemas import (
    AIInsightsResponse,
    AIOperationalMetrics,
    AIProductMetrics,
    CountByName,
)
from app.features.ai_jobs.models import AIJob

STUCK_AFTER_MINUTES = 15


class AIInsightsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_feedback(self, *, result_id: int, user_id: int, firm_id: int, category: str):
        result = await self.session.scalar(
            select(AIAssistanceResult).where(AIAssistanceResult.id == result_id, AIAssistanceResult.firm_id == firm_id)
        )
        if result is None:
            return None
        feedback = await self.session.scalar(
            select(AIResultFeedback).where(
                AIResultFeedback.result_id == result_id,
                AIResultFeedback.user_id == user_id,
                AIResultFeedback.firm_id == firm_id,
            )
        )
        if feedback is None:
            feedback = AIResultFeedback(result_id=result_id, user_id=user_id, firm_id=firm_id, category=category)
            self.session.add(feedback)
        else:
            feedback.category = category
        await self.session.flush()
        await self.session.refresh(feedback)
        return feedback

    async def insights(self, *, firm_id: int) -> AIInsightsResponse:
        jobs = list((await self.session.scalars(select(AIJob).where(AIJob.firm_id == firm_id))).all())
        results = list(
            (await self.session.scalars(select(AIAssistanceResult).where(AIAssistanceResult.firm_id == firm_id))).all()
        )
        feedback_rows = list(
            (await self.session.scalars(select(AIResultFeedback).where(AIResultFeedback.firm_id == firm_id))).all()
        )
        now = datetime.now(UTC)
        latencies: list[float] = []
        for job in jobs:
            completed_at = job.completed_at
            started_at = job.started_at
            if completed_at is not None and started_at is not None:
                latencies.append((completed_at - started_at).total_seconds() * 1000)
        successful = [job for job in jobs if job.status == "succeeded"]
        failed = [job for job in jobs if job.status == "failed"]
        errors = Counter(job.error_code for job in failed if job.error_code)
        input_tokens = sum(max(1, len(json.dumps(result.source_snapshot, sort_keys=True)) // 4) for result in results)
        output_tokens = sum(
            max(1, len(json.dumps(result.generated_content, sort_keys=True)) // 4) for result in results
        )
        stuck_cutoff = now - timedelta(minutes=STUCK_AFTER_MINUTES)
        stuck = sum(job.status in {"queued", "running"} and job.updated_at <= stuck_cutoff for job in jobs)
        statuses = Counter(result.review_status for result in results)
        edited = sum(
            result.reviewed_content is not None and result.reviewed_content != result.generated_content
            for result in results
        )
        converted = sum(bool(result.converted_actions) for result in results)
        regenerated = sum(result.source_snapshot.get("regenerates_result_id") is not None for result in results)
        feedback = Counter(row.category for row in feedback_rows)
        total = len(jobs)
        return AIInsightsResponse(
            generated_at=now,
            stuck_after_minutes=STUCK_AFTER_MINUTES,
            operational=AIOperationalMetrics(
                total_jobs=total,
                successful_jobs=len(successful),
                failed_jobs=len(failed),
                success_rate=round(len(successful) * 100 / total, 2) if total else 0,
                average_latency_ms=round(sum(latencies) / len(latencies), 2) if latencies else 0,
                estimated_input_tokens=input_tokens,
                estimated_output_tokens=output_tokens,
                cost_usd=None,
                cost_coverage_percent=0,
                retry_count=sum(max(0, job.attempt_count - 1) for job in jobs),
                stuck_jobs=stuck,
                errors=[CountByName(name=name, count=count) for name, count in sorted(errors.items())],
            ),
            product=AIProductMetrics(
                total_results=len(results),
                accepted_results=statuses["accepted"],
                partially_accepted_results=statuses["partially_accepted"],
                rejected_results=statuses["rejected"],
                pending_results=statuses["pending"],
                edited_results=edited,
                converted_results=converted,
                regenerated_results=regenerated,
                abandoned_results=statuses["pending"],
                feedback=[CountByName(name=name, count=count) for name, count in sorted(feedback.items())],
            ),
        )
