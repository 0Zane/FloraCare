![](https://github.com/0Zane/FloraCare/blob/65ee5e112a8adc63bb6f688a13ef02d72c68441e/assets/floracarebanner.png)
# FloraCare

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE) [![Open Source](https://img.shields.io/badge/Open%20Source-yes-brightgreen.svg)](LICENSE) [![Open Hardware](https://img.shields.io/badge/Open%20Hardware-yes-brightgreen.svg)](https://openhardware.science) [![MicroPython](https://img.shields.io/badge/MicroPython-ESP32-1abc9c.svg)](https://micropython.org) [![ESP32-S3](https://img.shields.io/badge/ESP32--S3-ESPRESSIF-ff6f00.svg)](https://www.espressif.com)

> Plant Tamagotchi — a connected device that monitors a plant's health using temperature, air humidity, soil moisture and light sensors. Built for the Trophées NSI 2026 (theme: Nature).

## 🎯 Goal

This project was created for the [Trophées NSI 2026](https://trophees-nsi.fr/) by @0Zane and @coderyansky. It offers a playful and educational experience: a digital companion that helps care for a plant by displaying real-time sensor data.

## 🏆 Awards

- **Regional Winner — Nature & Informatique**: FloraCare received the regional "Nature & Informatique" prize.
- **Nominated — Public Prize**: FloraCare was nominated for the Public Prize (see results).

See the official results: https://trophees-nsi.fr/resultats-2026

## 🧩 Hardware & Sensors

The project is based on a custom PCB driven by an **ESP32-S3**, chosen for native USB and enough power to run MicroPython.

| Component | Description | Interface / Protocol |
| :--- | :--- | :--- |
| **MCU** | ESP32-S3 Module | - |
| **PCB** | Custom design (Gerber files in `/hardware`) | - |
| **Display** | 1.9-inch 170x320 IPS color screen | **SPI** |
| **Temp / Humidity Sensor** | DHT22 | ADC |
| **Soil Moisture Sensor** | Analog soil moisture sensor | **ADC** |
| **Light Sensor** | BH1750 | **I2C** |
| **Power** | USB-C port | **5V DC -> 3.3V DC** |

> ⚡ The firmware runs on **MicroPython** and is intended to run continuously when powered via USB-C.

## 🚀 Quick Start

1. Flash MicroPython firmware to the ESP32-S3.
2. Copy all Python files to the microcontroller's flash.
3. Connect sensors to the pins defined in `main.py`.
4. Power via USB-C and observe readings on the display.

![](https://github.com/0Zane/FloraCare/blob/271e3f572fed55735c0cb3f5bc3360cbd0f8c488/assets/floracareproject.jpg)

## 🌐 WiFi Web Interface

FloraCare creates a WiFi Access Point (AP) that serves a web interface to view plant data remotely.

### WiFi connection info

| Parameter | Value |
| :--- | :--- |
| **SSID** | `FloraCare` |
| **Password** | `pythonTNSI2026` |
| **IP Address** | `192.168.4.1` |
| **Protocol** | **HTTP** (port 80) |

### Accessing the web interface

1. Connect your device (phone, tablet, PC) to the `FloraCare` WiFi network.
2. Use the password `pythonTNSI2026`.
3. Open a browser and go to `http://192.168.4.1`.
4. The web page shows real-time sensor values (temperature, humidity, light, soil moisture).

> 💡 Tip: the web interface is available while the ESP32-S3 is powered via USB-C.

## 📁 Repository Structure

- `src/`: MicroPython code (main, libraries, config)
- `hardware/`: Gerber and PCB files (KiCad)
- `README.md`: project documentation and user guide
- `presentation.md`: project presentation
- `requirements.txt`: required libraries
- `LICENSE`: GPL v3

## 🤝 Contributing

This project is open source and open hardware. Contributions are welcome.
## 📝 License

This project is licensed under **GPL v3**. See the `LICENSE` file for details.
