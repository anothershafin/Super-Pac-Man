# 🌀 Portal Pirate

![OpenGL](https://img.shields.io/badge/OpenGL-Graphics-blue)
![Python](https://img.shields.io/badge/Python-3.x-yellow)
![Course](https://img.shields.io/badge/Course-CSE423-orange)
![Project](https://img.shields.io/badge/Project-Academic-success)
![Status](https://img.shields.io/badge/Status-Constructing-orange)

---
**Portal Pirate** is a 2D/2.5D PyOpenGL-based game where strategy, timing, and spatial awareness are key to survival. Players navigate through restricted planes, create portals on walls, and outsmart enemies guarding treasures. Each level introduces higher difficulty with more complex mazes and enemies.

This project was developed as part of the **CSE423 (Computer Graphics)** course.

## 📌 Course Information
**Course:** CSE423 – Computer Graphics  
**Project Title:** Portal Pirate  
**Technology:** Python + OpenGL  
**Graphics Mode:** 3D  
**Template Used:** `3D_OpenGL_Intro.py` 

---

## 👥 Team Members
| Name | Student ID |
|------|------------|
| Shah Mohammad Zarif Abrar Ansari | 22201494 |
| Shafin Ahmed | 22201469 |
| Samiya Hossain Shabnam | 22201700 |



---

## 🎮 Game Features

1. Player can move freely within a plane while respecting movement restrictions.
2. Player can create portals on walls to navigate the maze strategically.
3. Enemies guard treasure boxes and patrol back and forth along fixed paths.
4. Portals can only be created to move the player to the side of the enemy.
5. If the player reaches the enemy’s side, the enemy will chase the player.
   - The player must retrieve the treasure before being caught.
6. Maze complexity and the number of enemies increase with each level.
7. Collecting all treasures opens a **Level Up Portal** to advance to the next level.

---

## 🧠 Gameplay Mechanics

- **Portals**: Core mechanic allowing instant movement across walls.
- **Enemy AI**:
  - Patrol Mode: Guards treasure.
  - Chase Mode: Activated when the player enters the enemy’s side.
- **Progression System**:
  - Increasing difficulty per level.
  - Multiple enemies in advanced stages.

---

## 🛠️ Technologies Used

- **Python**
- **PyOpenGL**
- **GLUT / OpenGL Utility Toolkit**
- **Computer Graphics Algorithms**
  - Transformations
  - Collision detection
  - Matrix operations

---

## ▶️ How to Run

1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/portal-pirate.git](https://github.com/anothershafin/Portal-Pirate.git)
   cd portal-pirate
   ```

2. Install required dependencies:
   ```bash
   pip install PyOpenGL PyOpenGL_accelerate
   ```

3. Run the game:
   ```bash
   python main.py
   ```

> ⚠️ Ensure you have a working OpenGL-compatible graphics driver.

---

## 📂 Project Structure (Example)

```
Portal-Pirate/
│
├── main.py
├── player.py
├── enemy.py
├── portal.py
├── level.py
├── assets/
│   ├── textures/
│   └── sounds/
├── README.md
└── requirements.txt
```

---

## 🎯 Learning Outcomes

- Practical understanding of PyOpenGL
- Game loop and event-driven programming
- Enemy behavior and state management
- Collision detection and transformations
- Applying computer graphics concepts in a real project

---

## 📜 License

This project is developed for **academic purposes** only.  
Feel free to explore, learn, and modify for educational use.

---

## ⭐ Acknowledgement

Special thanks to our course instructor and teaching assistants for guidance throughout the project.

---

Happy Gaming! 🏴‍☠️🌀

