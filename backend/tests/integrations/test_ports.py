import inspect

from app.integrations.broker import MessageBrokerPort
from app.integrations.jobs import JobSchedulerPort
from app.integrations.search import SearchIndexPort


def test_message_broker_port_declares_async_publish_operation() -> None:
    assert inspect.iscoroutinefunction(MessageBrokerPort.publish)


def test_job_scheduler_port_declares_async_enqueue_operation() -> None:
    assert inspect.iscoroutinefunction(JobSchedulerPort.enqueue)


def test_search_index_port_declares_async_upsert_and_delete_operations() -> None:
    assert inspect.iscoroutinefunction(SearchIndexPort.upsert_document)
    assert inspect.iscoroutinefunction(SearchIndexPort.delete_document)
