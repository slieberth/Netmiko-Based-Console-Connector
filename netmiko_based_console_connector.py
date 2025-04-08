import time
import threading
import paramiko
from netmiko.base_connection import BaseConnection


class ChannelWrapper:
    def __init__(self, chan):
        self.chan = chan

    def read_channel(self):
        if self.chan.recv_ready():
            return self.chan.recv(65535).decode(errors="ignore")
        return ""

    def write_channel(self, data):
        self.chan.send(data)

    def send(self, data):
        return self.chan.send(data)

    def recv(self, size=65535):
        return self.chan.recv(size)

    def recv_ready(self):
        return self.chan.recv_ready()

    def close(self):
        self.chan.close()


class NetmikoBasedConsoleConnectorViaAcs(BaseConnection):
    def __init__(self, channel, base_prompt="Router", **kwargs):
        wrapped_channel = ChannelWrapper(channel)
        self.channel = wrapped_channel
        self.remote_conn = wrapped_channel

        self.host = kwargs.get("host", "dummy-host")
        self.port = kwargs.get("port", 22)
        self.username = kwargs.get("username", "dummy")
        self.password = kwargs.get("password", "")
        self.device_type = kwargs.get("device_type", "cisco_ios")
        self.session_log = kwargs.get("session_log", None)
        self.global_delay_factor = kwargs.get("global_delay_factor", 1)

        self.encoding = "utf-8"
        self.RETURN = "\n"
        self.RESPONSE_RETURN = "\n"
        self.ansi_escape_codes = False
        self.fast_cli = False
        self.legacy_mode = False
        self.allow_auto_change = True
        self.read_timeout_override = kwargs.get("read_timeout_override", 0)
        self.session_timeout = kwargs.get("session_timeout", 60)
        self.timeout = kwargs.get("timeout", 60)
        self.session_log_file_mode = "write"
        self.delay_factor_compat = True
        self.global_cmd_verify = True
        self._session_locker = threading.Lock()
        self.disable_lf_normalization = False
        self._read_buffer = ""
        self._secrets_filter = None
        self.base_prompt = base_prompt

    @classmethod
    def connect_via_acs(cls, term_ip, port_number, username, password, **kwargs):
        print(f"Connecting to Acs Terminal Server ({term_ip}, port {port_number})...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(term_ip, username=username, password=password)
        print("Connection established.")

        chan = ssh.invoke_shell()
        print("Shell session started.")

        # Initial banner check
        time.sleep(2)
        banner = b""
        while chan.recv_ready():
            banner += chan.recv(4096)

        if b"<CTRL>Z" in banner:
            print("[INFO] Detected <CTRL>Z banner, sending RETURN...")
            chan.send("\n\r")
            time.sleep(1)

        prompt = cls.detect_prompt(chan) if hasattr(cls, "detect_prompt") else "Router"

        net_connect = cls(
            channel=chan,
            base_prompt=prompt,
            **kwargs
        )

        net_connect.clear_buffer()

        return net_connect, ssh

    def disconnect(self):
        try:
            print("Sending <CTRL>-Z and exit to close console session...")
            self.write_channel("\x1a")  # <CTRL>-Z
            time.sleep(1)
            self.write_channel("exit\n")
            time.sleep(1)
        except Exception as e:
            print(f"[WARN] Exception during disconnect: {e}")
        finally:
            self.remote_conn.close()


class NetmikoBasedConsoleConnectorViaAcsForCiscoCe(NetmikoBasedConsoleConnectorViaAcs):
    @staticmethod
    def detect_prompt(channel) -> str:
        channel.send("\n\r")
        time.sleep(1)
        buffer = b""
        while channel.recv_ready():
            buffer += channel.recv(4096)
        decoded = buffer.decode(errors="ignore")
        print("=== Console output ===")
        print(decoded)
        print("======================")

        lines = [line.strip() for line in decoded.splitlines() if line.strip()]
        for line in reversed(lines):
            if line.endswith("#") or line.endswith(">"):
                print(f"Detected prompt line: '{line}'")
                return line.strip("#>").strip()

        print("No valid prompt detected, falling back to 'Router'")
        return "Router"

    def disable_paging(self):
        try:
            self.write_channel(self.RETURN)
            time.sleep(1)
            self.clear_buffer()
            self.send_command_timing("terminal length 0", cmd_verify=False, read_timeout=5)
        except Exception as e:
            print(f"[WARN] disable_paging failed: {e}")


if __name__ == "__main__":
    term_ip = "192.168.2.78"
    port_number = "7001"
    username = f"admin:{port_number}"
    password = "avocent"

    kwargs = {
        "device_type": "cisco_ios",
        "session_log": None,
        "global_delay_factor": 1,
        "read_timeout_override": 5,
        "session_timeout": 120,
        "timeout": 120
    }

    net_connect, ssh = NetmikoBasedConsoleConnectorViaAcsForCiscoCe.connect_via_acs(
        term_ip=term_ip,
        port_number=port_number,
        username=username,
        password=password,
        **kwargs
    )

    net_connect.disable_paging()

    print("\nSending command: show version\n")
    output = net_connect.send_command_timing("show version", cmd_verify=False, read_timeout=10)
    print("=== Command Output ===")
    print(output)
    print("======================")

    net_connect.disconnect()
    ssh.close()
    print("Session closed.")
