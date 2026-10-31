import math
from dataclasses import dataclass

from flowforge.domain.exceptions import DomainError


class InvalidRetryPolicy(DomainError):
    """Raised when retry configuration is invalid."""


@dataclass(frozen=True, kw_only=True)
class RetryPolicy:
    max_attempts: int = 3
    initial_delay_seconds: float = 2.0
    backoff_multiplier: float = 2.0
    max_delay_seconds: float = 30.0

    def __post_init__(self) -> None:
        if type(self.max_attempts) is not int or self.max_attempts < 1:
            raise InvalidRetryPolicy("max_attempts must be a positive integer")

        for name in ("initial_delay_seconds", "backoff_multiplier", "max_delay_seconds"):
            value = getattr(self, name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise InvalidRetryPolicy(f"{name} must be a finite number")

        if self.initial_delay_seconds <= 0:
            raise InvalidRetryPolicy("initial_delay_seconds must be positive")

        if self.backoff_multiplier < 1:
            raise InvalidRetryPolicy("backoff_multiplier must be at least 1")

        if self.max_delay_seconds < self.initial_delay_seconds:
            raise InvalidRetryPolicy("max_delay_seconds must be >= initial_delay_seconds")

    def should_retry(self, attempts_completed: int) -> bool:
        if type(attempts_completed) is not int or attempts_completed < 0:
            raise ValueError("attempts_completed must be non-negative")

        return attempts_completed < self.max_attempts

    def delay_for_retry(self, retry_number: int) -> float:
        if type(retry_number) is not int or not 1 <= retry_number < self.max_attempts:
            raise ValueError("Invalid retry number")

        exponent = retry_number - 1
        log_delay = math.log(self.initial_delay_seconds) + exponent * math.log(
            self.backoff_multiplier
        )
        if log_delay >= math.log(self.max_delay_seconds):
            return float(self.max_delay_seconds)

        delay = self.initial_delay_seconds * self.backoff_multiplier**exponent
        return float(min(delay, self.max_delay_seconds))
