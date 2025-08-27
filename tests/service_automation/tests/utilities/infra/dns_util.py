import socket
import time
from loguru import logger


def wait_for_dns(hostname, timeout=180, interval=5):
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            socket.gethostbyname(hostname)
            logger.debug(f"DNS for {hostname} is resolvable.")
            logger.debug(f"Resolved IP: {socket.gethostbyname(hostname)}")
            return True
        except socket.error:
            time.sleep(interval)
            logger.error(f"DNS for {hostname} is not resolvable after {time.time()} seconds.")
    return False
