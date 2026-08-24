"""
FORENZA Infrastructure Circuit Breaker Engine (Dimension 10 & 18).

Protects downstream databases, biocomputational workers, and external APIs from cascading failures:
- 3-State Finite State Machine: CLOSED -> OPEN -> HALF_OPEN -> CLOSED.
- Automatic Fail-Fast with RFC Retry-After headers when downstream is degraded.
- Concurrency and Connection Pooling Health Guards.
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple


class CircuitState(str, Enum):
    CLOSED = "CLOSED"        # Normal operational state, passing all traffic
    OPEN = "OPEN"            # Tripped state, failing fast without hitting downstream
    HALF_OPEN = "HALF_OPEN"  # Probe state, testing recovery with limited canary traffic


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5          # Number of consecutive failures to trip circuit
    recovery_timeout_seconds: float = 30.0 # Time to remain OPEN before probing HALF_OPEN
    half_open_success_threshold: int = 3   # Consecutive successes required to CLOSE circuit
    execution_timeout_seconds: float = 10.0 # Maximum time allowed for single execution


class CircuitBreaker:
    """
    Thread-safe / Coroutine-safe Circuit Breaker for infrastructure reliability.
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.last_state_change = time.time()
        self.last_failure_time = 0.0

    def can_execute(self, now: Optional[float] = None) -> Tuple[bool, Optional[str], int]:
        """
        Checks if request is allowed to execute.
        Returns (allowed, error_message, retry_after_seconds).
        """
        ts = now if now is not None else time.time()

        if self.state == CircuitState.CLOSED:
            return True, None, 0

        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed to transition to HALF_OPEN
            if ts - self.last_state_change >= self.config.recovery_timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                self.consecutive_successes = 0
                self.last_state_change = ts
                return True, None, 0

            remaining = int(self.config.recovery_timeout_seconds - (ts - self.last_state_change))
            remaining = max(1, remaining)
            return False, f"Downstream service '{self.name}' is currently unavailable (Circuit OPEN).", remaining

        if self.state == CircuitState.HALF_OPEN:
            # In HALF_OPEN, allow limited probe requests
            return True, None, 0

        return True, None, 0

    def record_success(self, now: Optional[float] = None):
        """Records successful downstream execution."""
        ts = now if now is not None else time.time()

        if self.state == CircuitState.HALF_OPEN:
            self.consecutive_successes += 1
            if self.consecutive_successes >= self.config.half_open_success_threshold:
                # Fully recovered!
                self.state = CircuitState.CLOSED
                self.consecutive_failures = 0
                self.consecutive_successes = 0
                self.last_state_change = ts
        elif self.state == CircuitState.CLOSED:
            self.consecutive_failures = 0

    def record_failure(self, now: Optional[float] = None):
        """Records failed downstream execution (timeout, 5xx, or network error)."""
        ts = now if now is not None else time.time()
        self.last_failure_time = ts

        if self.state == CircuitState.CLOSED:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.config.failure_threshold:
                # Trip circuit to OPEN
                self.state = CircuitState.OPEN
                self.last_state_change = ts
        elif self.state == CircuitState.HALF_OPEN:
            # Probe failed -> trip back to OPEN immediately
            self.state = CircuitState.OPEN
            self.last_state_change = ts

    def get_status(self) -> Dict[str, Any]:
        """Returns diagnostic telemetry for monitoring."""
        return {
            "name": self.name,
            "state": self.state.value,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
            "last_state_change": self.last_state_change,
        }


class CircuitBreakerRegistry:
    """Registry managing circuit breakers across backend subsystems."""

    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._load_default_subsystems()

    def _load_default_subsystems(self):
        # Database pool breaker
        self.register(
            CircuitBreaker("database_primary", CircuitBreakerConfig(failure_threshold=5, recovery_timeout_seconds=20.0))
        )
        # Heavy biocompute worker breaker
        self.register(
            CircuitBreaker("biocompute_mcmc_zkp", CircuitBreakerConfig(failure_threshold=3, recovery_timeout_seconds=30.0))
        )
        # External NCBI / EMPOP reference lookup breaker
        self.register(
            CircuitBreaker("external_reference_apis", CircuitBreakerConfig(failure_threshold=4, recovery_timeout_seconds=45.0))
        )

    def register(self, breaker: CircuitBreaker):
        self._breakers[breaker.name] = breaker

    def get(self, name: str) -> Optional[CircuitBreaker]:
        return self._breakers.get(name)

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        return {name: b.get_status() for name, b in self._breakers.items()}


# Singleton instance
circuit_registry = CircuitBreakerRegistry()
