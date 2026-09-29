---
id: page-21
title: "VPN & Remote Access Setup"
space: HR-IT
owner: "IT Operations"
status: current
document_type: procedure
department: hr-it
labels: [vpn, remote-access, how-to]
last_updated: 2026-07-06
effective_date: 2026-07-06
related: []
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/HR-IT/VPN+Remote+Access+Setup"
---

# VPN & Remote Access Setup

This guide explains how to set up and connect to Meridian's VPN for remote work and secure network access.

## Prerequisites

- A valid Meridian employee account
- Your company-issued laptop (Windows, Mac, or Linux)
- 15 minutes for initial setup

## VPN client installation

### Windows and Mac

1. Download **Meridian VPN Client** (v5.2 or later) from the HR-IT Portal: https://it.meridian.example/vpn-downloads
2. Run the installer and follow the prompts
3. Restart your computer after installation
4. Launch the VPN client from your applications menu

### Linux

1. Install OpenVPN: `sudo apt-get install openvpn` (Debian/Ubuntu) or `sudo yum install openvpn` (RHEL/CentOS)
2. Download the config file from the HR-IT Portal
3. Connect: `sudo openvpn --config meridian-vpn.conf`
4. Enter your Meridian credentials when prompted

## Connecting to the VPN

1. Launch the VPN client
2. Select **"Meridian Remote Access"** from the server list
3. Enter your Meridian username and password
4. Click **"Connect"**
5. Wait for the status to change to **"Connected"**

Once connected, you're on Meridian's internal network and can access all resources as if you were in the office.

## Disconnecting

1. Click **"Disconnect"** in the VPN client
2. Your connection to internal resources will end, but your internet access remains unaffected

## Troubleshooting

**"Connection refused"**
- Ensure you're using the latest VPN client version
- Check that your Meridian account password is correct
- Verify your internet connection is working

**"Timeout after connecting"**
- You may have a local firewall blocking VPN traffic; contact HR-IT

**"Slow performance over VPN"**
- VPN performance depends on your internet speed; close bandwidth-heavy applications (video streaming)
- Connect to a wired network if possible (WiFi can be slower)

**Still having issues?**
- Email **vpn-support@meridian.example** with your OS version, VPN client version, and the error message

## Best practices

- Always disconnect from the VPN when you're done working (security best practice)
- Do not share your VPN credentials with anyone, including colleagues
- Keep your VPN client updated; security patches are released regularly
- Use a strong password and enable two-factor authentication on your Meridian account

## VPN bandwidth limits

Meridian's VPN has fair-use limits:

- Streaming video over VPN is not permitted (bandwidth-intensive)
- Large file transfers should be batched during off-peak hours (7 PM–7 AM)
- Do not use the VPN for personal internet browsing or torrenting

Violations may result in VPN access suspension.
