"""
Locust Load Testing for SIRA API

Tests system performance with 50+ concurrent users submitting queries.
Measures error rates, response times, and throughput.

Usage:
    # Run with Locust web UI
    locust -f load_test.py --host=http://localhost:8080
    
    # Run headless with 50 users
    locust -f load_test.py --host=http://localhost:8080 --users 50 --spawn-rate 5 --run-time 5m --headless

Requirements:
    - locust
    - requests
"""

import random
import time
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner


# Test queries for load testing
TEST_QUERIES = [
    "What is 2 + 2?",
    "Explain photosynthesis",
    "Who was the first president of the United States?",
    "What is the capital of France?",
    "Write a Python function to reverse a string",
    "How does gravity work?",
    "What causes seasons on Earth?",
    "Explain the water cycle",
    "What is machine learning?",
    "How do computers store data?",
    "What is DNA?",
    "Explain supply and demand",
    "What is the Pythagorean theorem?",
    "How does the internet work?",
    "What is climate change?"
]


class SIRAUser(HttpUser):
    """Simulates a user interacting with SIRA API"""
    
    # Wait between 1-3 seconds between tasks
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        # Create a session
        try:
            response = self.client.post("/sessions", json={
                "user_id": f"load-test-user-{self.environment.runner.user_count}"
            })
            if response.status_code == 200:
                self.session_id = response.json().get("session_id")
            else:
                self.session_id = None
        except Exception as e:
            print(f"Failed to create session: {e}")
            self.session_id = None
    
    @task(10)
    def submit_query(self):
        """Submit a query to SIRA (most common task)"""
        query = random.choice(TEST_QUERIES)
        
        with self.client.post(
            "/query",
            json={
                "query": query,
                "session_id": self.session_id
            },
            catch_response=True,
            name="/query [POST]"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("response"):
                    response.success()
                else:
                    response.failure("No response in body")
            elif response.status_code == 500:
                response.failure(f"Server error: {response.status_code}")
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(3)
    def get_metrics_summary(self):
        """Fetch metrics summary"""
        with self.client.get(
            "/metrics/summary",
            catch_response=True,
            name="/metrics/summary [GET]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(2)
    def get_core_metrics(self):
        """Fetch core metrics"""
        with self.client.get(
            "/metrics/core",
            catch_response=True,
            name="/metrics/core [GET]"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "metrics" in data:
                    response.success()
                else:
                    response.failure("Missing metrics in response")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def get_session_history(self):
        """Fetch session history"""
        if not self.session_id:
            return
        
        with self.client.get(
            f"/sessions/{self.session_id}/history",
            catch_response=True,
            name="/sessions/{id}/history [GET]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # Session might not exist yet, that's ok
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")


# Global stats tracking
stats = {
    "total_requests": 0,
    "failed_requests": 0,
    "total_response_time": 0,
    "min_response_time": float('inf'),
    "max_response_time": 0
}


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track request statistics"""
    stats["total_requests"] += 1
    stats["total_response_time"] += response_time
    
    if response_time < stats["min_response_time"]:
        stats["min_response_time"] = response_time
    if response_time > stats["max_response_time"]:
        stats["max_response_time"] = response_time
    
    if exception:
        stats["failed_requests"] += 1


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print summary statistics when test stops"""
    print("\n" + "="*60)
    print("LOAD TEST SUMMARY")
    print("="*60)
    
    if stats["total_requests"] > 0:
        error_rate = (stats["failed_requests"] / stats["total_requests"]) * 100
        avg_response = stats["total_response_time"] / stats["total_requests"]
        
        print(f"Total Requests: {stats['total_requests']:,}")
        print(f"Failed Requests: {stats['failed_requests']:,}")
        print(f"Error Rate: {error_rate:.2f}%")
        print(f"Avg Response Time: {avg_response:.0f} ms")
        print(f"Min Response Time: {stats['min_response_time']:.0f} ms")
        print(f"Max Response Time: {stats['max_response_time']:.0f} ms")
        
        # Check AC-089: < 5% error rate
        if error_rate < 5.0:
            print(f"\n✓ AC-089 PASSED: Error rate {error_rate:.2f}% < 5%")
        else:
            print(f"\n✗ AC-089 FAILED: Error rate {error_rate:.2f}% >= 5%")
    
    print("="*60 + "\n")


# Custom test configuration
class LoadTestConfig:
    """Configuration for different load test scenarios"""
    
    @staticmethod
    def light_load():
        """Light load: 10 users"""
        return {
            "users": 10,
            "spawn_rate": 2,
            "run_time": "2m"
        }
    
    @staticmethod
    def medium_load():
        """Medium load: 25 users"""
        return {
            "users": 25,
            "spawn_rate": 5,
            "run_time": "3m"
        }
    
    @staticmethod
    def heavy_load():
        """Heavy load: 50 users (AC-089 requirement)"""
        return {
            "users": 50,
            "spawn_rate": 5,
            "run_time": "5m"
        }
    
    @staticmethod
    def stress_test():
        """Stress test: 100 users"""
        return {
            "users": 100,
            "spawn_rate": 10,
            "run_time": "5m"
        }


if __name__ == "__main__":
    """
    Direct execution example (for testing)
    In practice, use: locust -f load_test.py --host=http://localhost:8080
    """
    print("SIRA Load Test Configuration")
    print("-" * 40)
    print("\nAvailable test scenarios:")
    print("1. Light Load: 10 users, 2m")
    print("2. Medium Load: 25 users, 3m")
    print("3. Heavy Load: 50 users, 5m (AC-089)")
    print("4. Stress Test: 100 users, 5m")
    print("\nRun with locust:")
    print("  locust -f load_test.py --host=http://localhost:8080 --users 50 --spawn-rate 5 --run-time 5m --headless")
