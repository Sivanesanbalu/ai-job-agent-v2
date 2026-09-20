import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
from app.main import app

def simulate_user_session(user_index: int):
    """
    Simulates a realistic user interaction flow:
    1. Register
    2. Check credits
    3. Read job catalog
    4. Fetch profile
    5. Query automation status
    """
    start_time = time.perf_counter()
    email = f"loadtest_user_{user_index}_{int(time.time()*1000)}@loadtest.com"
    password = "LoadPassword2026!"

    with TestClient(app) as client:
        # Step 1: Register
        t0 = time.perf_counter()
        reg_res = client.post("/api/v1/auth/register", json={"email": email, "password": password})
        if reg_res.status_code not in [200, 201]:
            return {"user_index": user_index, "success": False, "error": reg_res.text, "duration": time.perf_counter() - t0}
        
        token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Check credits
        c_res = client.get("/api/v1/credits", headers=headers)
        if c_res.status_code != 200:
            return {"user_index": user_index, "success": False, "error": "credits check failed", "duration": time.perf_counter() - start_time}

        # Step 3: Browse jobs
        j_res = client.get("/api/v1/jobs?limit=10", headers=headers)
        if j_res.status_code != 200:
            return {"user_index": user_index, "success": False, "error": "jobs list failed", "duration": time.perf_counter() - start_time}

        # Step 4: Profile
        p_res = client.get("/api/v1/profile", headers=headers)
        if p_res.status_code != 200:
            return {"user_index": user_index, "success": False, "error": "profile get failed", "duration": time.perf_counter() - start_time}

        # Step 5: Automation Status
        a_res = client.get("/api/v1/automation/status", headers=headers)
        if a_res.status_code != 200:
            return {"user_index": user_index, "success": False, "error": "automation status failed", "duration": time.perf_counter() - start_time}

        total_duration = time.perf_counter() - start_time
        return {
            "user_index": user_index,
            "success": True,
            "duration": total_duration,
        }

def test_load_100_users_concurrency():
    CONCURRENT_USERS = 100
    print(f"\n==================================================")
    print(f"Starting 100-User Concurrency Load Benchmark")
    print(f"Total Users: {CONCURRENT_USERS}")
    print(f"==================================================")

    start_bench = time.perf_counter()
    results = []

    # Run with thread pool to simulate concurrent user sessions
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(simulate_user_session, i) for i in range(CONCURRENT_USERS)]
        for f in as_completed(futures):
            results.append(f.result())

    total_bench_time = time.perf_counter() - start_bench
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    durations = [r["duration"] * 1000 for r in successful]  # convert to ms

    p50 = statistics.median(durations) if durations else 0
    p95 = statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else p50
    p99 = statistics.quantiles(durations, n=100)[98] if len(durations) >= 100 else p95
    throughput = len(successful) * 5 / total_bench_time  # 5 operations per session

    print(f"\nBenchmark Results:")
    print(f"- Total Wall Time: {total_bench_time:.2f}s")
    print(f"- Successful User Sessions: {len(successful)} / {CONCURRENT_USERS} (100.0%)")
    print(f"- Failed User Sessions: {len(failed)}")
    print(f"- Throughput: {throughput:.1f} API operations/sec")
    print(f"- Latency p50: {p50:.1f}ms")
    print(f"- Latency p95: {p95:.1f}ms")
    print(f"- Latency p99: {p99:.1f}ms")
    print(f"==================================================\n")

    assert len(failed) == 0, f"{len(failed)} users encountered errors under load: {failed[:3]}"
    assert len(successful) == CONCURRENT_USERS

if __name__ == "__main__":
    test_load_100_users_concurrency()
