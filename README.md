# Game Room Project

This is a personal project aimed at creating a website where people can play games like **Tusmo**, **Skyjo**, and more.  
Players can join a private room using a **game code** and play together in real time.

---

## 🎮 How It Works
1. One player creates a room.
2. A **room code** is generated.
3. Other players enter the room code to join automatically.
4. Once everyone has joined, the group chooses a game and starts playing.
5. All game data (e.g., duration, points, etc.) is stored in a database for tracking.

---

## 🔐 Access
I am still considering whether to:
- Use **accounts** for login,  
- Or allow access directly via the device **IP address**.  

---

## 🗄 Database
- The project uses **MySQL** databases (no external servers required).  
- A special database called **LEXIQUE** is included, provided by [Bilgé Kimyonok](https://github.com/WhiteFangs/lexique.sql).  

### View the Database
To explore the database manually:
```bash
psql -h 127.0.0.1 -p 5432 -U admin -d visitorjournal