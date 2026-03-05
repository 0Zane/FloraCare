# TNSI

Ce projet des trophéesNSI a été réalisé avec micropython


## 🛠 Matériel & Composants 

Le projet repose sur un circuit personnalisé (Custom PCB) piloté par un ESP32-S3, choisi pour ses capacités de gestion native de l'USB et sa puissance de calcul.

| Composant | Description | Interface / Protocole |
| :--- | :--- | :--- |
| **MCU** | ESP32-S3 Module | - |
| **PCB** | Custom Design (Gerber files in `/hardware`) | - |
| **Écran** | LCD 1.3" ou 2.0" (ST7789) | **SPI** |
| **Capteur Temp.** | ... | **I2C / OneWire** |
| **Capteur Sol** | Soil Moisture Sensor (...) | **Analogique (ADC)** |
| **Capteur Lumière** | ... | **Analogique / I2C** |
| **Alimentation** | Port USB-C (LDO 3.3V intégré) | **5V DC** |
| **Boîtier** | Case conçu sur mesure (Fichiers STL) | **Impression 3D** |

> **Note :** Ce projet est conçu pour être alimenté en continu via USB-C, éliminant ainsi les cycles de charge de batterie pour une surveillance 24/7.
