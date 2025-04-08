# 🧰 Experimental Netmiko Console Connector via Avocent Terminal Server

This module extends [Netmiko](https://github.com/ktbyers/netmiko) to support **console access through terminal servers**, such as reverse SSH connections (e.g., `ssh admin:7001@192.168.x.x`). It's useful for lab automation, hardware bring-up, or remote out-of-band access scenarios.

## ✨ Features

- ✅ Works over active `paramiko` `invoke_shell()` sessions
- ✅ Compatible with Netmiko’s full command interface
- ✅ Automatically detects Avocent `<CTRL>Z` banner
- ✅ Auto-detects prompt (e.g. `R1>`, `Switch#`)
- ✅ Graceful disconnect with `<CTRL>-Z` and `exit`
- ✅ Vendor-specific subclass: `Cisco CE` with `disable_paging`

---

## 🧪 Example

### Code

```python
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

    net_connect, ssh = NetmikoBasedConsoleConnectorViaAvocentForCiscoCe.connect_via_avocent(
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
```

Output 
```shell
Connecting to Acs Terminal Server (192.168.2.78, port 7001)...
Connection established.
Shell session started.
[INFO] Detected <CTRL>Z banner, sending RETURN...
=== Console output ===

R1>
R1>
R1>
======================
Detected prompt line: 'R1>'

Sending command: show version

=== Command Output ===
Cisco IOS Software, C870 Software (C870-ADVENTERPRISEK9-M), Version 12.4(24)T3, RELEASE SOFTWARE (fc2)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2010 by Cisco Systems, Inc.
Compiled Tue 23-Mar-10 18:21 by prod_rel_team

ROM: System Bootstrap, Version 12.3(8r)YI4, RELEASE SOFTWARE

R1 uptime is 2 days, 11 minutes
System returned to ROM by power-on
System image file is "flash:c870-adventerprisek9-mz.124-24.T3.bin"

...

Configuration register is 0x2102

======================
Sending <CTRL>-Z and exit to close console session...
Session closed.
```
---

## 🧩 Class Structure

```python
class NetmikoBasedConsoleConnectorViaAvocent(BaseConnection)
class NetmikoBasedConsoleConnectorViaAvocentForCiscoCe(NetmikoBasedConsoleConnectorViaAvocent)
```

---

## 🧠 Notes

- This approach allows reuse of the full Netmiko command API via console sessions.
- The prompt detection is vendor-aware and overrideable.
- Currently optimized for Cisco-like CLI and Avocent reverse-SSH style access.
- Easily extensible for other vendors or console server types (e.g., Digi, Lantronix).

---

## 🙌 Credit

Built on top of [Netmiko](https://github.com/ktbyers/netmiko) – special thanks to @ktbyers and the Netmiko community!

---
