# 🌱 FloraCare — Présentation du projet

## 1. Présentation globale du projet

L’idée du projet est née grâce à Arnaud (Zane), en s’appuyant sur ses connaissances en électronique et en Python, en lien avec le thème proposé.

Nous nous sommes posé la problématique suivante :  
**Comment aider les humains à s’occuper de leurs plantes de manière ludique et intuitive ?**

L’objectif du projet *FloraCare* est donc de simplifier la compréhension des besoins d’une plante en lui donnant une forme de “communication” avec l’humain, grâce à des capteurs et une interface claire.

---

## 2. Organisation du travail

### 👥 Équipe
- **Arnaud D. élève de 1ère NSI amateur de C++ et python et d'éléctronique.**
- **Alexander K. élève de 1ère NSI passionné de python**

### 🛠️ Répartition des rôles

**Arnaud D. :**
- Développement en Python  
- Conception du circuit imprimé (PCB)  
- Intégration des fonctions capteurs dans le code  
- Mise en place du Wi-Fi et interface web via ESP  


**Alexander K. :**
- Développement en Python  
- Intégration des fonctions capteurs dans le code  
- Programmation de l’écran (interface graphique avancée)  

### Temps passé sur le projet :
Arnaud à entendu parler du projet en Février et à commencer à chercher un équipier, puis après avoir trouvé Alexander, nous avons travaillé durant tout le mois de mars.

---

## 3. Étapes du projet

1. **Idéation et organisation**
   - Formation du groupe  ()
   - Réflexion (~2h) sur le concept et la répartition des tâches  

2. **Développement parallèle**
   - Arnaud : conception rapide du PCB (contrainte de temps)  
   - Alexander : début du développement de l’interface écran  

3. **Choix des capteurs (étape critique)**
   - Compatibilité avec MicroPython  
   - Coût abordable  
   - Facilité d’intégration sur PCB  
   - Pertinence des données  

4. **Structuration du code**
   - Organisation pour lisibilité et performance  

5. **Développement avancé**
   - Arnaud : Wi-Fi + interface web  
   - Alexander : finalisation écran + capteurs  

6. **Assemblage**
   - Réception du PCB  
   - Soudure et tests matériels  

---

## 4. Validation et fonctionnement

### ✅ État du projet
- Circuit imprimé fonctionnel  
- Code global fonctionnel  


### 🧪 Méthodes de test

- **Tests matériels :**
  - Utilisation d’un multimètre  
  - Vérification de l'état physique (température, robustesse du circuit imprimé)

- **Tests logiciels :**
  - Debug via console (Thonny IDE)  
  - Ajout de messages `print`  

- **Validation des données :**
  - Comparaison avec un thermomètre  
  - Tests logiques  
  - Utilisation réelle du système  

### ⚠️ Difficultés rencontrées

- Choix des capteurs  
- Programmation de l’écran en MicroPython  
- Mise en place d’un point d’accès Wi-Fi  
- Conception rapide du PCB (1 semaine)

---

## 5. Ouverture et perspectives

### 🚀 Améliorations possibles
- Ajout d’un boîtier finalisé  
- Intégration de davantage de types de plantes  

### 🔍 Analyse critique
Le projet répond aux contraintes du concours avec une solution originale.  
L’utilisation de ressources externes (drivers, documentation) a permis d’accélérer le développement.  
L’intelligence artificielle a été utilisée de manière stratégique pour des tâches secondaires (HTML, descriptions).

### 🧠 Compétences développées
- Travail en équipe avec GitHub  
- Rigueur en électronique (pas de “ça marche à peu près”)  
- Application des compétences en python aquises en NSI dans un contexte concret  
- Compréhension du protocole HTTP  

### 🤝 Démarche d’inclusion
Le projet vise à rendre le soin des plantes accessible à tous, y compris aux débutants, grâce à une interface simple et compréhensible.

---

## ⚙️ Mise en fonctionnement

⚠️ **Important :**  
Importer **tous les fichiers dans la mémoire flash** avant exécution (possible via ThonnyIDE).

---

## 📚 Sources

- https://docs.python.org/fr/3/howto/sockets.html  
- https://randomnerdtutorials.com/micropython-wi-fi-manager-esp32-esp8266/  
- https://requests.readthedocs.io/en/latest/  
- https://documentation.espressif.com/esp32-s3_datasheet_en.pdf

- https://github.com/lvgl-micropython/lvgl_micropython