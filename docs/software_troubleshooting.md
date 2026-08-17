# Software Troubleshooting Guide

## Application Crashes or Freezes

**Immediate Steps:**
1. Save any open work in other applications.
2. End the process: Ctrl+Shift+Esc → find application → End Task.
3. Restart the application.
4. If crash persists, restart the computer.

**Investigation:**
1. Check Event Viewer: Windows Logs → Application for error details.
2. Check available disk space — crashes can occur when C: drive is full.
3. Run application as Administrator to rule out permission issues.
4. Reinstall the application if issue persists.

---

## Microsoft Office Issues

**Outlook Not Opening:**
1. Run Outlook in Safe Mode: `outlook.exe /safe`
2. If it opens, disable add-ins: File → Options → Add-ins → COM Add-ins → Go → uncheck all.
3. Repair Office: Control Panel → Programs → Microsoft 365 → Change → Quick Repair.

**Word/Excel File Won't Open:**
1. Check if file is already open by another user (shared drive).
2. Right-click file → Open With → choose application.
3. Use Open and Repair: File → Open → Browse → select file → dropdown arrow next to Open → Open and Repair.

**Teams Audio/Video Issues:**
1. Check Teams audio device: Settings → Devices → ensure correct speaker/mic selected.
2. Test with: Settings → Devices → Make a test call.
3. Restart Teams: System tray → right-click Teams → Quit → reopen.
4. Update Teams to latest version.

---

## Email Issues

**Cannot Send/Receive Email:**
1. Check internet connection.
2. Verify Outlook is not in Offline Mode: Send/Receive → Work Offline (should NOT be checked).
3. Check spam/junk folder for expected emails.
4. Verify mailbox is not full: File → Info → Mailbox Settings.
5. Re-enter email password if prompted.
6. Contact IT if authentication errors appear.

**Large Email Rejected:**
1. Maximum attachment size: 25MB.
2. Use company SharePoint/OneDrive to share large files.
3. Send link instead of attachment.

---

## Slow Computer Performance

**Quick Fixes:**
1. Restart the computer — clears memory and applies pending updates.
2. Close unused applications and browser tabs.
3. Check Disk Usage: Task Manager → Performance → Disk (>90% is problematic).
4. Run Disk Cleanup: Start → Disk Cleanup → select C: → clean system files.

**Deeper Investigation:**
1. Task Manager → CPU/Memory — identify high-usage processes.
2. Check for malware: run Windows Defender full scan.
3. Check startup items: Task Manager → Startup tab → disable non-essential items.
4. If HDD, consider requesting SSD upgrade through IT.

---

## Software Installation

**Standard Software:**
All standard software is available through the Company Software Portal at:
https://software.company.com

**Requesting New Software:**
1. Submit request via IT Help Desk portal.
2. Include business justification.
3. IT will evaluate and install within 5 business days.

**Admin Rights:**
Users do not have local admin rights by default.
Request temporary admin access for approved installs through IT.
