# 🌱 FloraCare — Project Presentation

## 1. Overall Project Overview

The project idea was born thanks to Zane, leveraging his knowledge of electronics and Python in connection with the proposed theme.

We asked ourselves the following question:  
**How can we help humans care for their plants in a playful and intuitive way?**

The objective of the *FloraCare* project is therefore to simplify understanding a plant's needs by giving it a form of "communication" with humans, through sensors and a clear interface.

---

## 2. Work Organization

### 👥 Team
- **Zane** — 1st year CS student, enthusiast of C++, Python, and electronics.
- **CoderyanskyK** — 1st year CS student, passionate about Python.

### 🛠️ Role Distribution

**Zane:**
- Python development  
- PCB design (circuit board)  
- Sensor function integration into the code  
- Wi-Fi setup and web interface via ESP  


**Coderyansky:**
- Python development  
- Sensor function integration into the code  
- Display programming (advanced graphical interface)  

### Time spent on the project:
Zane heard about the project in February and began looking for a teammate. After finding Coderyansky, we worked throughout March.

---

## 3. Project Stages

1. **Ideation and organization**
   - Team formation  
   - Reflection (~2h) on the concept and task distribution  

2. **Parallel development**
   - Zane: rapid PCB design (time constraint)  
   - CoderyanskyK: beginning screen interface development  

3. **Sensor selection (critical step)**
   - Compatibility with MicroPython  
   - Affordable cost  
   - Easy PCB integration  
   - Data relevance  

4. **Code structuring**
   - Organization for readability and performance  

5. **Advanced development**
   - Zane: Wi-Fi + web interface  
   - CoderyanskyK: screen finalization + sensors  

6. **Assembly**
   - PCB reception  
   - Soldering and hardware testing  

---

## 4. Validation and Operation

### ✅ Project Status
- Functional circuit board  
- Functional global code  


### 🧪 Testing Methods

- **Hardware tests:**
  - Use of a multimeter  
  - Verification of physical condition (temperature, circuit board robustness)

- **Software tests:**
  - Debug via console (Thonny IDE)  
  - Addition of `print` messages  

- **Data validation:**
  - Comparison with a thermometer  
  - Logical tests  
  - Real-world system usage  

### ⚠️ Challenges Encountered

- Sensor selection  
- Display programming in MicroPython  
- Setting up a Wi-Fi access point  
- Rapid PCB design (1 week)

---

## 5. Openings and Perspectives

### 🚀 Possible Improvements
- Addition of a finalized enclosure  
- Integration of more plant types  

### 🔍 Critical Analysis
The project addresses competition constraints with an original solution.  
The use of external resources (drivers, documentation) accelerated development.  
Artificial intelligence was used strategically for secondary tasks (HTML, descriptions).

### 🧠 Skills Developed
- Teamwork with GitHub  
- Rigor in electronics (no "it works roughly")  
- Application of Python skills acquired in CS in a real-world context  
- Understanding of HTTP protocol  

### 🤝 Inclusive Approach
The project aims to make plant care accessible to everyone, including beginners, through a simple and understandable interface.

---

## ⚙️ Deployment

⚠️ **Important:**  
Import **all files into flash memory** before execution (possible via ThonnyIDE).

---

## 📚 Sources

- https://docs.python.org/fr/3/howto/sockets.html  
- https://randomnerdtutorials.com/micropython-wi-fi-manager-esp32-esp8266/  
- https://requests.readthedocs.io/en/latest/  
- https://documentation.espressif.com/esp32-s3_datasheet_en.pdf
- https://github.com/lvgl-micropython/lvgl_micropython
