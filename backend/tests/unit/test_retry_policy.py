import math

import pytest

from flowforge.domain.retry_policy import InvalidRetryPolicy, RetryPolicy


def test_default_retry_policy() -> None:
    policy = RetryPolicy()

    assert policy.max_attempts == 3
    assert policy.initial_delay_seconds == 2.0
    assert policy.backoff_multiplier == 2.0
    assert policy.max_delay_seconds == 30.0


def test_should_retry_before_limit() -> None:
    policy = RetryPolicy(max_attempts=3)

    assert policy.should_retry(0)
    assert policy.should_retry(1)
    assert policy.should_retry(2)
    assert not policy.should_retry(3)


def test_exponential_backoff() -> None:
    policy = RetryPolicy(max_attempts=5, initial_delay_seconds=2, backoff_multiplier=2)

    assert policy.delay_for_retry(1) == 2
    assert policy.delay_for_retry(2) == 4
    assert policy.delay_for_retry(3) == 8
    assert policy.delay_for_retry(4) == 16


def test_delay_is_capped() -> None:
    policy = RetryPolicy(max_attempts=5, initial_delay_seconds=10, max_delay_seconds=15)

    assert policy.delay_for_retry(3) == 15


@pytest.mark.parametrize("attempts", [0, -1, True, 1.5])
def test_invalid_attempt_limit(attempts: object) -> None:
    with pytest.raises(InvalidRetryPolicy):
        RetryPolicy(max_attempts=attempts)


@pytest.mark.parametrize("attempts", [-1, True, 1.5])
def test_invalid_completed_attempts(attempts: object) -> None:
    policy = RetryPolicy()

    with pytest.raises(ValueError):
        policy.should_retry(attempts)


@pytest.mark.parametrize("retry_number", [0, -1, 3, True])
def test_retry_number_must_be_valid(retry_number: object) -> None:
    policy = RetryPolicy(max_attempts=3)

    with pytest.raises(ValueError):
        policy.delay_for_retry(retry_number)


@pytest.mark.parametrize(
    "field_name, value",
    [
        ("initial_delay_seconds", 0),
        ("initial_delay_seconds", -1),
        ("initial_delay_seconds", math.nan),
        ("initial_delay_seconds", math.inf),
        ("backoff_multiplier", 0.5),
        ("backoff_multiplier", math.nan),
        ("backoff_multiplier", math.inf),
        ("max_delay_seconds", math.nan),
        ("max_delay_seconds", math.inf),
    ],
)
def test_invalid_retry_configuration(field_name: str, value: float) -> None:
    with pytest.raises(InvalidRetryPolicy):
        RetryPolicy(**{field_name: value})


def test_max_delay_cannot_be_lower_than_initial_delay() -> None:
    with pytest.raises(InvalidRetryPolicy):
        RetryPolicy(initial_delay_seconds=10, max_delay_seconds=5)


def test_single_attempt_policy_has_no_retries() -> None:
    policy = RetryPolicy(max_attempts=1)

    assert not policy.should_retry(1)

    with pytest.raises(ValueError):
        policy.delay_for_retry(1)


def test_backoff_multiplier_one_produces_constant_delay() -> None:
    policy = RetryPolicy(max_attempts=4, initial_delay_seconds=3, backoff_multiplier=1)

    assert policy.delay_for_retry(1) == 3
    assert policy.delay_for_retry(2) == 3
    assert policy.delay_for_retry(3) == 3


def test_large_exponential_backoff_is_capped_without_overflow() -> None:
    policy = RetryPolicy(
        max_attempts=100_000, initial_delay_seconds=2, backoff_multiplier=100, max_delay_seconds=30
    )

    assert policy.delay_for_retry(99_999) == 30
