import subprocess
import time

class WireMockManager:
    def __init__(self):
        self.process = None

    def start(self):
        self.process = subprocess.Popen([
            "java", "-jar", "wiremock-standalone-2.35.0.jar",
            "--port", "8080", "--root-dir", "wiremock"
        ])
        time.sleep(2)  # Wait for server to start

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
