# 🌱 PlantCare XP – Virtual Plant Health Monitor

## 📌 Description
**PlantCare XP** is a Python-based interactive project that simulates plant health monitoring, inspired by gamified apps like *Talking Tom*.  
Each plant has **XP (experience points)** and **health levels** that dynamically change based on user actions and environmental factors like rain, soil quality, and fertilizers.  

---

## ✨ Features

### 🪴 Plant Health System
- Plants have **XP/health points** shown as a progress bar or percentage.  
- Health changes dynamically based on care and conditions.

### 🌦️ Dynamic Factors
- **Rainfall** → Increases hydration and boosts health.  
- **Soil Quality** → Determines how effective feeding/fertilizer will be.  
- **Feeding & Fertilizers** → Boost XP and plant growth.  
- **Neglect** → Health decreases if the plant isn’t cared for.  

### 🎮 User Interactions
- Actions: *Water Plant*, *Feed Plant*, *Fertilize*, *Check Soil*.  
- Plant mood changes (😊 happy, 😐 neutral, 😢 sad) based on health.  

### 🏆 Gamification
- **Level System** → Plants grow to higher levels as XP increases.  
- **Achievements/Badges** → Unlock milestones like “Green Thumb 🌿” or “Master Gardener 🌻”.  
- **Daily Rewards** → Incentives for regular plant care.  

### 🗄️ Database (Supabase)
- Stores:
  - Plant stats (health, XP, levels)  
  - User profiles (multiple players supported)  
  - Interaction logs (watering times, feeding actions, etc.)  
- Syncs plant data across sessions.  

### 🖥️ Frontend (Python CLI / GUI)
- **CLI Mode** → Text-based menus and ASCII health bars.  
- **GUI Mode (Tkinter/PyQt)** → Plant image changes state based on health.  

### 📊 Reports & Insights
- View plant growth history with graphs (via Matplotlib).  
- Notifications/reminders when plant health is low.  

---

## 📂 Project Structure

```
PLANTCARE XP/
|
|---src/            #core application logic
|   |---logic.py    #Business logic and task
operations
|   |__db.py        #Database operations
|
|---api/            #Backend API
|   |__main.py      #FastAPI endpoints
|
|---frontend/       #Frontend Application
|   |__app.py       #Steamlit web interface
|
|___requirements.txt  #Python Dependencies
|
|___README.md       #Project documentation
|
|___.env            #Python Variables
```

---

## 🚀 Quick Start

### ✅ Prerequisites
- Python **3.8+**  
- A **Supabase account**  
- Git (for cloning and pushing code)  

---

### 1. Clone or Download the Project
```bash
# Option 1: Clone with Git

git clone https://github.com/Koushikgoud008/Python-Full-Stack-Project.git

# Option 2: Download and Extract the ZIP file

# Install all required Pythin packages
pip install -r requirements.txt
```
### 3. Set up supabase Database

1.Create a supabase Project:

2.create the tasks Table:

-Go to the SQL Editor in your Supabase Dashborad
-Run this SQL command

``` sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE plants (
    plant_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    plant_name VARCHAR(100) NOT NULL,
    level INT DEFAULT 1,
    xp INT DEFAULT 0,
    health INT DEFAULT 100,  -- scale 0–100
    soil_quality INT DEFAULT 50, -- scale 0–100
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE TABLE interactions (
    interaction_id SERIAL PRIMARY KEY,
    plant_id INT REFERENCES plants(plant_id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL, -- e.g., 'water', 'fertilize', 'feed', 'rain'
    effect_value INT,                 -- + or - effect on health/XP
    created_at TIMESTAMP DEFAULT NOW()
);

```

3. **Get your Credentials:

### 4. Configure Environment Variables

1. Create a `.env` file in the project root

2.Add your Supabase credentials to `.env`:
```
SUPABASE_URL = 
SUPABASE_KEY = 
```
### 5. Run the Application

## streamlit Frontend
```
streamlit run frontend/app.py

The app will open in your browser at `http://localhost:8501`
```
## FastAPI Backend
```
cd api
python main.py
```
The API will be avsilsble at `http://localhost:8000`

## How to use 


## 🛠️ Tech Stack
- **Backend** → FastAPI (python REST API framework)  
- **Frontend** → streamlit (python web framework)
- **Database** → Supabase (Postgres)  
- **Language** → Python 3.8+

---

### Key Components

1. **`src/db.py`**: Data operations 
    - handles all CURD operations with Supabase

2. **`src/logic.py`**: Business logic 
    -Task validation and processing

## Troubleshooting

## common Issues

1.

### 🚀 Future Enhancments
- Integration with **IoT sensors** (soil moisture, sunlight, humidity).
- **Weather API** to simulate real-time rainfall conditions.
- **Social Mode** → Share plants and compare growth with friends.

## 🏆 Gamification
- **Level System** → Plants grow to higher levels as XP increases.
- **Achievements/Badges** → Unlock milestones like “Green Thumb 🌿” or “Master Gardener 🌻”.
- **Daily Rewards** → Incentives for regular plant care.

## support 

If you encounter any issues or have questions:
-Mail : koushikgoud008@gmail.com
-contact : 123456789