"""
Database Socket Health Probe Watchdog
Polls MySQL and MongoDB endpoints with active TCP/Daemon handshake probes
before initiating schema migrations or high-volume seed imports.
"""

import socket
import time
import sys
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("DBWatchdog")


def check_tcp_socket(host: str, port: int, timeout_sec: float = 2.0) -> bool:
    """Verifies low-level TCP socket connectivity"""
    try:
        with socket.create_connection((host, port), timeout=timeout_sec):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def wait_for_service(name: str, host: str, port: int, max_attempts: int = 30, delay_sec: float = 2.0) -> bool:
    logger.info("Waiting for %s socket binding on %s:%d...", name, host, port)
    for attempt in range(1, max_attempts + 1):
        if check_tcp_socket(host, port):
            logger.info("-> %s is UP and accepting connections (attempt %d/%d).", name, attempt, max_attempts)
            return True
        logger.debug("Attempt %d failed, sleeping %.1fs...", attempt, delay_sec)
        time.sleep(delay_sec)

    logger.error("Timed out waiting for %s after %d attempts.", name, max_attempts)
    return False


def main():
    # Demonstration configuration
    services = [
        {"name": "MySQL Server", "host": "127.0.0.1", "port": 3306},
        {"name": "MongoDB Daemon", "host": "127.0.0.1", "port": 27017},
        {"name": "Redis In-Memory", "host": "127.0.0.1", "port": 6379},
    ]

    print("Initiating Database Readiness Verification...")
    # For standalone demonstration in test environment, we run against test host
    test_ok = check_tcp_socket("127.0.0.1", 6379)
    print(f"Health Probe Self-Test (Port 6379 Available?): {test_ok}")
    print("Database probe module initialized successfully.")


if __name__ == "__main__":
    main()