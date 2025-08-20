'''
This function demonstrates fault tolerance for a data processing task (e.g., fetching and processing sensor data), incorporating exception handling, logging, 
and a safe fallback to ensure system stability. It follows the no-outage principle by gracefully handling failures and maintaining state integrity.
'''
import logging
import time
from typing import Optional
from contextlib import contextmanager
import requests
# Configure structured logging for observability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
@contextmanager
def timeout(seconds: int):
    """Context manager for timeout handling."""
    start_time = time.time()
    try:
        yield
    except Exception as e:
        if time.time() - start_time > seconds:
            logger.error(f"Operation timed out after {seconds}s: {e}")
            raise TimeoutError("Operation exceeded time limit")
        raise
def fetch_and_process_data(url: str, max_retries: int = 3, timeout_seconds: int = 5) -> Optional[dict]:
    """
    Fetches data from a URL and processes it with fault-tolerant mechanisms.
    Args:
        url: Endpoint to fetch data from.
        max_retries: Number of retry attempts for transient failures.
        timeout_seconds: Timeout for the request.
    Returns:
        Processed data or None if all retries fail.
    """
    attempt = 0
    fallback_data = {"status": "degraded", "data": []}  # Safe fallback
    while attempt < max_retries:
        try:
            with timeout(timeout_seconds):
                response = requests.get(url, timeout=timeout_seconds)
                response.raise_for_status()  # Raise exception for bad status codes
                logger.info(f"Successfully fetched data from {url}")
                return response.json()  # Process and return data
        except (requests.RequestException, TimeoutError) as e:
            attempt += 1
            logger.warning(f"Attempt {attempt}/{max_retries} failed: {e}")
            if attempt == max_retries:
                logger.error(f"All retries exhausted for {url}. Falling back to safe mode.")
                return fallback_data
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            logger.error(f"Unexpected error: {e}. Falling back to safe mode.")
            return fallback_data
    return fallback_data
# Example usage
if __name__ == "__main__":
    data = fetch_and_process_data("https://example.com/api/data")
    print(f"Processed data: {data}")
