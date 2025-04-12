import subprocess
import os
import select
import time
import tempfile
from models import ConnectionState

class VPNManager:
    def __init__(self):
        self.active_vpns = {}

    def connect(self, button, config_path, username, password, sudo_password):
        try:
            # Create temporary auth file
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as auth_file:
                auth_file.write(f"{username}\n{password}")
                auth_file_path = auth_file.name

            try:
                # Get full path to OpenVPN
                openvpn_path = subprocess.check_output(['which', 'openvpn']).decode().strip()
                print(f"DEBUG: Using OpenVPN at {openvpn_path}")
                
                command = [
                    "sudo", "-S",
                    openvpn_path,
                    "--config", config_path,
                    "--auth-user-pass", auth_file_path,
                    "--verb", "4"
                ]
                
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # Send sudo password
                process.stdin.write(f"{sudo_password}\n")
                process.stdin.flush()
                
                # Monitor process output with timeout
                timeout = 30
                start_time = time.time()
                
                while True:
                    if process.poll() is not None:
                        print(f"DEBUG: Process ended with return code: {process.poll()}")
                        stderr_output = process.stderr.read()
                        if stderr_output:
                            print(f"ERROR: {stderr_output}")
                        break
                    
                    if time.time() - start_time > timeout:
                        print("DEBUG: Connection timeout")
                        process.terminate()
                        break
                    
                    reads = [process.stdout.fileno(), process.stderr.fileno()]
                    ret = select.select(reads, [], [], 0.5)
                    
                    for fd in ret[0]:
                        if fd == process.stdout.fileno():
                            line = process.stdout.readline()
                            if line:
                                print(f"OpenVPN: {line.strip()}")
                                if "Attempting to establish TCP connection" in line:
                                    button.observer.set_state(ConnectionState.CONNECTING)
                                elif "PENDING" in line:
                                    button.observer.set_state(ConnectionState.AUTHENTICATING)
                                elif "Initialization Sequence Completed" in line:
                                    self.active_vpns[config_path] = process
                                    button.observer.set_state(ConnectionState.CONNECTED)
                                    return True
                        elif fd == process.stderr.fileno():
                            error = process.stderr.readline()
                            if error:
                                print(f"ERROR: {error.strip()}")
                                if "permission denied" in error.lower():
                                    button.observer.set_state(ConnectionState.DISCONNECTED)
                                    return False
                
            finally:
                # Clean up auth file
                os.unlink(auth_file_path)
                print("DEBUG: Auth file cleaned up")
                
        except Exception as e:
            print(f"DEBUG: Critical error in connect: {str(e)}")
            button.observer.set_state(ConnectionState.DISCONNECTED)
            return False

    def disconnect(self, config_path, sudo_password):
        if config_path in self.active_vpns:
            process = self.active_vpns[config_path]
            try:
                # Send SIGTERM to the OpenVPN process
                process.terminate()
                process.wait(timeout=5)
                return True
            except subprocess.TimeoutExpired:
                # If process doesn't terminate, force kill it
                process.kill()
                return True
            finally:
                del self.active_vpns[config_path]
        return False