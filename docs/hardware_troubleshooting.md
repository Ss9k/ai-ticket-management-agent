# Hardware Troubleshooting Guide

## Computer Won't Turn On

**Steps:**
1. Verify power cable is firmly connected to both PC and wall outlet.
2. Check that the power strip or UPS is switched on.
3. Hold power button for 10 seconds to force shutdown, then press again.
4. For laptops: remove battery (if removable), hold power 30 seconds, reconnect and try.
5. Check for LED indicators — solid orange may indicate power supply issue.
6. Escalate to hardware team if no response after above steps.

---

## Monitor Display Issues

**Black Screen:**
1. Check monitor power cable and data cable (HDMI/DisplayPort/VGA).
2. Press monitor power button to wake from sleep.
3. Try Win + P to switch display mode (Duplicate/Extend/Projector only).
4. Try connecting monitor to a different port on the PC.
5. Boot into Safe Mode to determine if it's a driver issue.

**Resolution/Scaling Issues:**
1. Right-click Desktop → Display Settings.
2. Set recommended resolution.
3. Update display driver via Device Manager.

---

## Keyboard or Mouse Not Working

**USB Devices:**
1. Unplug and replug into a different USB port.
2. Try on another computer to confirm device works.
3. Check Device Manager for driver errors (yellow exclamation).
4. Uninstall and reinstall device driver.

**Wireless Devices:**
1. Replace batteries.
2. Ensure USB receiver is plugged in.
3. Press pairing button on device.
4. Move receiver to a USB port away from USB 3.0 interference.

---

## Printer Troubleshooting

**Printer Offline:**
1. Check printer is powered on and cable/WiFi connected.
2. Open Control Panel → Devices and Printers → right-click printer → See what's printing.
3. Click Printer menu → Uncheck "Use Printer Offline".
4. Restart Print Spooler: Run `services.msc`, find Print Spooler, restart.
5. Re-add printer if above steps fail.

**Print Jobs Stuck in Queue:**
1. Open Services (services.msc).
2. Stop "Print Spooler" service.
3. Navigate to `C:\Windows\System32\spool\PRINTERS` and delete all files.
4. Start "Print Spooler" service again.
5. Try printing again.

---

## Laptop Battery Issues

**Battery Not Charging:**
1. Try a different power adapter if available.
2. Check charging port for debris.
3. Run Battery Report: `powercfg /batteryreport` in Command Prompt.
4. If battery health below 40%, request replacement through IT.

**Short Battery Life:**
1. Set Power Plan to "Balanced" or "Power Saver".
2. Reduce screen brightness.
3. Disable Bluetooth and WiFi when not in use.
4. Check Battery Report for high-drain applications.
