![](https://github.com/0Zane/FloraCare/blob/65ee5e112a8adc63bb6f688a13ef02d72c68441e/assets/floracarebanner.png)
# FloraCare

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE) [![Open Source](https://img.shields.io/badge/Open%20Source-yes-brightgreen.svg)](LICENSE) [![Open Hardware](https://img.shields.io/badge/Open%20Hardware-yes-brightgreen.svg)](https://openhardware.science) [![MicroPython](https://img.shields.io/badge/MicroPython-ESP32-1abc9c.svg)](https://micropython.org) [![ESP32-S3](https://img.shields.io/badge/ESP32--S3-ESPRESSIF-ff6f00.svg)](https://www.espressif.com)

> **Tamagotchi de plante** — un objet connecté qui surveille la santé d'une plante avec des capteurs de température, d'humidité de l'air, d'humidité du sol et de lumière, construit pour les trophées NSI 2026 (thème **Nature**).


<br>
<br>

## 🎯 Objectif

Ce projet a été réalisé pour les [**trophées NSI 2026**](https://trophees-nsi.fr/) par **@0Zane** et **@coderyansky**. Il propose une experience ludique et éducative : un compagnon numérique qui aide à prendre soin d'une plante en affichant des données en temps réel selon l'état des capteurs.



## 🧩 Matériel & Capteurs

Le projet repose sur un circuit imprimé personnalisé (PCB) piloté par un **ESP32-S3**, choisi pour ses capacités USB natif et sa puissance pour exécuter Micropython.

| Composant | Description | Interface / Protocole |
| :--- | :--- | :--- |
| **MCU** | ESP32-S3 Module | - |
| **PCB** | Conception personnalisée (Gerber dans `/hardware`) | - |
| **Écran** | 1.9-inch 170X320 IPS color screen | **SPI** |
| **Capteur Temp. / Humidité** | DHT22 | ADC |
| **Capteur Humidité Sol** | Capteur d'humidité du sol analogique | **ADC** |
| **Capteur Lumière** | BH1750 | **I2C** / |
| **Alimentation** | Port USB-C  | **5V DC -> 3.3V DC** |

> ⚡ Ce projet tourne sous **Micropython** et est prévu pour fonctionner en continu via USB-C.



## 🚀 Démarrage rapide

1. Flasher le firmware MicroPython sur l'ESP32-S3.
2. Copier le contenu de `src/` sur la mémoire flash du microcontrôleur.
3. Connecter les capteurs sur les broches définies dans.
4. Brancher en USB-C et observer les lectures sur l'écran.



## 🌐 Interface Web WiFi

FloraCare crée un **point d'accès WiFi (AP)** pour permettre l'accès à distance aux données de la plante via une interface web.

### Informations de connexion WiFi

| Paramètre | Valeur |
| :--- | :--- |
| **SSID** | `FloraCare` |
| **Mot de passe** | `pythonTNSI2026` |
| **Adresse IP** | `192.168.4.1` |
| **Protocole** | **HTTP** (Port 80) |

### Accès à l'interface web

1. Connectez votre appareil (téléphone, tablette, PC) au réseau WiFi **FloraCare**
2. Utilisez le mot de passe : **pythonTNSI2026**
3. Ouvrez un navigateur web et accédez à : `http://192.168.4.1`
4. Vous verrez l'interface affichant les données en temps réel de vos capteurs (température, humidité, lumière, humidité du sol)

> 💡 **Conseil** : L'interface est accessible tant que le module ESP32-S3 est alimenté via USB-C.


## 📁 Structure du dépôt

- `src/` : code Micropython (main, bibliothèques, config)
- `hardware/` : fichiers Gerber et PCB (KiCad)
- `README.md` : documentation du projet et mode d'emploi
- `presentation.md` : présentation du projet
- `requirements.txt` : Librairies utilisées à installer
- `LICENSE` : GPL v3



## 🤝 Contribution

Ce projet est **open source et open hardware**. N'hésitez pas à proposer des améliorations :

- Améliorer la gestion des capteurs ou ajouter des nouveaux capteurs
- Ajouter une interface web / API pour consulter les données à distance
- Optimiser la consommation et la réservation de l'écran



## 📝 Licence

Ce projet est distribué sous licence **GPL v3**. Voir le fichier `LICENSE` pour plus de détails.
