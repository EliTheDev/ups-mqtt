# UPS Monitor Setup

Quick setup guide to configure a Linux device (Raspberry Pi 2B in this example) as a UPS monitor with MQTT forwarding.

Repository based on dniklewicz/ups-mqtt.

## Prerequisites

- Raspberry Pi 2B
- MicroSD card (8GB+)
- Ethernet cable (Pi 2B has no WiFi)
- UPS with USB connection

## 1. Initial Pi Setup
*Getting the basic operating system onto your Pi*

1. **Flash OS**: Use Raspberry Pi Imager to install **Legacy Full** version of Raspberry Pi OS
2. **Set username**: Configure username as `eng` during imaging
3. **Boot and connect**: Connect Pi via ethernet and boot up

## 2. Network Setup (if needed)
*Making sure your Pi can reach the internet to download software*

Since the Pi 2B lacks WiFi, you may need to share internet through ethernet for initial setup.

## 3. Install Dependencies
*Getting the software tools we need to talk to UPS devices and send data*

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install nut nano python3-pip -y
```

## 4. Configure Network UPS Tools (NUT)
*Teaching your Pi how to communicate with your specific UPS device*

### Configure UPS Hardware
*Tell NUT exactly what UPS you have and how to talk to it*
```bash
sudo nano /etc/nut/ups.conf
```

Add your UPS configuration:
```ini
[<UPS_NAME>]
driver = "<DRIVER>"
port = /dev/ttyUSB0
desc = "<DESCRIPTION>"
```

### Configure NUT Server
*Allow other devices on your network to ask this Pi about UPS status*
```bash
sudo nano /etc/nut/upsd.conf
```

Add:
```
LISTEN 0.0.0.0 3493
```

### Setup NUT User
*Create login credentials for accessing UPS data*
```bash
sudo nano /etc/nut/upsd.users
```

Add:
```ini
[eng]
password = <PASSWORD>
upsmon primary
```

### Enable NUT Server Mode
*Turn on the service that shares UPS data with other devices*
```bash
sudo nano /etc/nut/nut.conf
```

Set:
```
MODE=netserver
```

Restart NUT service:
```bash
sudo systemctl restart nut-server
```

## 5. Setup Static IP
*Give your Pi a fixed network address so other devices can always find it*

```bash
sudo nano /etc/dhcpcd.conf
```

Add:
```
interface eth0
static ip_address=xx.xx.xxx.xxx/24
static routers=xx.xx.xxx.x
static domain_name_servers=xx.xx.xxx.x
```

## 6. Install UPS-MQTT Bridge
*Download the custom software that forwards UPS data to your MQTT broker*

```bash
git clone https://github.com/EliTheDev/ups-mqtt.git
cd ./ups-mqtt
sudo nano conf/config.ini
```

Fill in the configuration values as needed.

## 7. Create Systemd Service
*Set up the Pi to automatically run the UPS monitoring software on boot*

```bash
sudo nano /etc/systemd/system/ups-mqtt.service
```

Add:
```ini
[Unit]
Description=UPS MQTT monitor
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/python3 /home/eng/ups-mqtt/ups-mqtt2.py
WorkingDirectory=/home/eng/ups-mqtt
User=eng
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ups-mqtt.service
sudo systemctl start ups-mqtt.service
sudo reboot
```

## 8. Verify Installation
*Check that everything is working and your UPS data is being sent properly*

Check service status:
```bash
sudo systemctl status ups-mqtt.service
```

The service should be running and automatically forwarding UPS data to MQTT.

## Troubleshooting

- Check logs: `journalctl -u ups-mqtt.service -f`
- Verify NUT connection: `upsc <UPS_NAME>`
- Test MQTT connectivity from your MQTT broker
