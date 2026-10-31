from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4

from flowforge.domain.exceptions import DomainError
from flowforge.domain.retry_policy import RetryPolicy


class InvalidStepTransition(DomainError): ...


class StepExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    RETRYING = "retrying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(kw_only=True)
class StepExecution:
    step_id: UUID
    retry_policy: RetryPolicy
    id: UUID = field(default_factory=uuid4)
    status: StepExecutionStatus = field(default=StepExecutionStatus.PENDING, init=False)
    attempts: int = field(default=0, init=False)
    last_error: str | None = field(default=None, init=False)
    retry_delay_seconds: float | None = field(default=None, init=False)

    def start(self) -> None:
        if self.status not in (StepExecutionStatus.PENDING, StepExecutionStatus.RETRYING):
            raise InvalidStepTransition(f"Cannot start step in {self.status} state")

        if self.attempts >= self.retry_policy.max_attempts:
            raise InvalidStepTransition("Maximum attempts already reached")

        self.attempts += 1
        self.status = StepExecutionStatus.RUNNING
        self.retry_delay_seconds = None

    def succeed(self) -> None:
        if self.status != StepExecutionStatus.RUNNING:
            raise InvalidStepTransition("Only a running step can succeed")

        self.status = StepExecutionStatus.SUCCEEDED
        self.last_error = None

    def fail(self, error: str, *, retryable: bool) -> None:
        if self.status != StepExecutionStatus.RUNNING:
            raise InvalidStepTransition("Only a running step can fail")

        self.last_error = error

        if retryable and self.retry_policy.should_retry(self.attempts):
            self.retry_delay_seconds = self.retry_policy.delay_for_retry(self.attempts)
            self.status = StepExecutionStatus.RETRYING
        else:
            self.retry_delay_seconds = None
            self.status = StepExecutionStatus.FAILED
