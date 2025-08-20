import time
import random

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=5):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # Possible states: CLOSED, OPEN, HALF-OPEN

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
            else:
                raise Exception("Circuit is OPEN. Call blocked.")

        try:
            result = func(*args, **kwargs)
            self._reset()
            return result
        except Exception as e:
            self._record_failure()
            raise e

    def _record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def _reset(self):
        self.failure_count = 0
        self.state = "CLOSED"

# Simulated flaky service
def unreliable_service():
    if random.random() < 0.5:
        raise Exception("Service failed!")
    return "Success!"

# Usage
cb = CircuitBreaker()

for i in range(10):
    try:
        print(cb.call(unreliable_service))
    except Exception as e:
        print(f"Attempt {i+1}: {e}")
    time.sleep(1)
