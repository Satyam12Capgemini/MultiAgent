# Router Troubleshooting and Setup Guide

## 1. Quick Setup and Installation
To set up your Dual-Band Mesh Router Pro or Extender:
1. Connect the power adapter to an AC outlet and plug the power connector into the back of your router.
2. Connect one end of the included RJ-45 Ethernet cable to your broadband modem and the other end to the blue Internet/WAN port.
3. Wait approximately 90 seconds until the Power LED glows steady solid green.
4. On your computer or mobile device, search for the default Wi-Fi network named `SupportCopilot_Net_2.4G` or `SupportCopilot_Net_5G`.
5. Enter the default Wi-Fi password printed on the bottom product label (default: `AdminWireless2026`).

## 2. Resolving Frequent Disconnections and Reboots
If your router keeps restarting or disconnecting randomly:
- **Power supply verification:** Ensure you are using the official 12V 2A power adapter. Third-party or underpowered adapters cause sudden brownouts and reboots during heavy traffic.
- **Overheating check:** Keep the router in an open, well-ventilated area away from direct sunlight, heaters, and enclosed TV cabinets. Clean any dust from the side ventilation grills.
- **Firmware update:** Navigate to `http://192.168.1.1` in your browser. Log in with your admin credentials, go to **System Tools > Firmware Upgrade**, and install version v2.4.1 or later which resolves a memory leak issue.

## 3. Factory Reset Instructions
If you forgot your administrator password or experience persistent network degradation:
1. Locate the physical **Reset** pinhole button on the rear panel next to the power switch.
2. While the router is powered on, use a straightened paperclip to press and hold the **Reset** button continuously for 10 to 12 seconds.
3. Release the button when all front panel LEDs blink amber simultaneously.
4. The router will restart with factory default settings in approximately 2 minutes.

## 4. Port Forwarding and NAT Configuration
For online gaming or hosting local servers:
- Access the management portal at `http://192.168.1.1`.
- Go to **Advanced Settings > Forwarding > Virtual Servers**.
- Click **Add New**, enter the local device IP address (e.g., `192.168.1.150`), internal and external port numbers (e.g., `8080`), select TCP/UDP protocol, and click **Save**.
