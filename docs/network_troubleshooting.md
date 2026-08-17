# Network Troubleshooting Guide

## Cannot Connect to Internet

**Symptoms:** Browser shows "No Internet Connection", ping to 8.8.8.8 fails.

**Steps:**
1. Check physical cable connection or WiFi signal strength.
2. Run `ipconfig /release` then `ipconfig /renew` to renew DHCP lease.
3. Run `netsh winsock reset` and restart the computer.
4. Check DNS: Run `nslookup google.com`. If it fails, set DNS to 8.8.8.8 manually.
5. Disable and re-enable the network adapter in Device Manager.
6. Check with IT if the DHCP server is reachable.

**Escalate if:** Multiple machines affected in the same subnet.

---

## VPN Connection Issues

**Symptoms:** VPN client shows "Authentication Failed" or "Timeout".

**Steps:**
1. Verify your username and password are correct.
2. Ensure VPN client software is up to date.
3. Try connecting on a different network (e.g., mobile hotspot).
4. Clear VPN cache: navigate to AppData and delete VPN profile folder.
5. Check if MFA token is correct and not expired.
6. Contact IT to verify your VPN account has not been disabled.

**Common error codes:**
- Error 691: Authentication failure — check credentials.
- Error 800: Connection timeout — check firewall rules.
- Error 619: Port blocked — contact network team.

---

## Slow Network Performance

**Steps:**
1. Run speed test at speedtest.net to measure actual bandwidth.
2. Check Task Manager for applications consuming bandwidth.
3. Run `tracert google.com` to identify bottlenecks.
4. Ensure no large backups or updates running in background.
5. Contact IT if speed is consistently below SLA thresholds.

---

## Network Drive Not Accessible

**Steps:**
1. Verify you are connected to the corporate network or VPN.
2. Try accessing by IP instead of hostname: `\\192.168.1.100\share`.
3. Check Windows Credential Manager for stale cached credentials.
4. Run `net use * /delete` to clear mapped drives, then reconnect.
5. Ensure your account has permission to the share.
