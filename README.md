## 🔌 Netmiko Extension: Console Access via Avocent Terminal Server and Netmiko Library

### Overview

This custom module provides an experimental `BaseConnection` subclass that allows Netmiko to manage devices via **console access behind Avocent-style terminal servers**.

### Why?
In our test-setup the access to console ports is provided by avocent console servers . This code enables full Netmiko compatibility with those console sessions, making it possible to reuse standard `send_command*()` and automation logic.

---

### Key Features

- ✅ **Avocent login logic** with detection of `<CTRL>Z` banners and session wake-up via `\n\r`.
- ✅ **Custom Paramiko-to-Netmiko channel wrapper** using `ChannelWrapper`.
- ✅ **Base prompt detection** for Cisco-style prompts (`Router>`, `Switch#`, etc.).
- ✅ **Vendor-specific subclass** with `disable_paging()` for Cisco CE.
- ✅ **Clean disconnect** method: sends `<CTRL>-Z` and `exit` before closing session.
- ✅ Fully Netmiko-compatible command handling (`send_command`, `send_command_timing`, etc.).

---

### Class Structure

```python
class NetmikoBasedConsoleConnectorViaAvocent(BaseConnection)
class NetmikoBasedConsoleConnectorViaAvocentForCiscoCe(NetmikoBasedConsoleConnectorViaAvocent)
