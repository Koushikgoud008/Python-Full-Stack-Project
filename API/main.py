import uvicorn
import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json

# Add parent directory to path to allow import from src/
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.db import SupabaseDB
from src.logic import (
    apply_action, 
    apply_decay,  
    calculate_level_xp, 
    get_plant_mood
)

# Load environment variables (Supabase keys)
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    # A standard way to handle missing environment variables in FastAPI/Uvicorn
    print("FATAL ERROR: SUPABASE_URL or SUPABASE_KEY is missing in .env file.")
    sys.exit(1)

# Initialize Database Client
db_client = SupabaseDB(supabase_url, supabase_key)

# --- Pydantic Schemas ---

class UserSchema(BaseModel):
    username: str
    email: str

class PlantCreateSchema(BaseModel):
    user_id: int
    plant_name: str

class PlantActionSchema(BaseModel):
    plant_id: int
    action_type: str

class PlantResponseSchema(BaseModel):
    plant_id: int
    user_id: int
    plant_name: str
    level: int
    xp: int
    xp_needed: int
    health: int
    soil_quality: int
    mood: str
    last_updated: str


# --- FastAPI Application ---
app = FastAPI(title="PlantCare XP API", version="1.0")

@app.get("/")
def read_root():
    """Basic health check endpoint."""
    return {"status": "ok", "service": "PlantCare XP API"}

# --- User Endpoints ---

@app.post("/users/register")
def register_user(user_data: UserSchema):
    """Register a new user or retrieve an existing one."""
    existing_user = db_client.get_user_by_username(user_data.username)
    if existing_user:
        return {"user": existing_user, "message": f"Welcome back, {existing_user['username']}!"}
    
    new_user = db_client.create_user(user_data.username, user_data.email)
    if new_user:
        return {"user": new_user, "message": f"User '{new_user['username']}' registered successfully!"}
    
    raise HTTPException(status_code=500, detail="Failed to register user.")

# --- Plant Endpoints ---

@app.post("/plants/create", response_model=PlantResponseSchema)
def create_plant(plant_data: PlantCreateSchema):
    """Create a new plant for a user."""
    # Initial state calculation
    initial_xp = 0
    initial_level, initial_xp_needed = calculate_level_xp(initial_xp)
    initial_health = 100
    initial_mood = get_plant_mood(initial_health)

    # Note: Supabase handles the `created_at` and `last_updated` default values
    
    new_plant = db_client.create_plant(
        plant_data.user_id,
        plant_data.plant_name,
        initial_level,
        initial_xp,
        initial_health,
        50, # default soil quality
        initial_mood
    )
    if new_plant:
        # Add the derived state to the response (xp_needed)
        new_plant['xp_needed'] = initial_xp_needed
        return new_plant
    
    raise HTTPException(status_code=500, detail="Failed to create plant.")

@app.get("/plants/{user_id}", response_model=List[PlantResponseSchema])
def get_user_plants(user_id: int):
    """
    Retrieve all plants for a user, applying decay to each one
    before returning them.
    """
    plants = db_client.get_plants_by_user(user_id)
    if not plants:
        return []
    
    updated_plants = []
    for plant in plants:
        # 1. Apply Decay to the plant state 
        decayed_plant = apply_decay(plant)
        
        # 2. Update the plant state in the database immediately
        db_client.update_plant_state(decayed_plant['plant_id'], decayed_plant)
        
        # 3. Add derived stats for the frontend response
        level, xp_needed = calculate_level_xp(decayed_plant['xp'])
        decayed_plant['level'] = level
        decayed_plant['xp_needed'] = xp_needed
        decayed_plant['mood'] = get_plant_mood(decayed_plant['health'])

        updated_plants.append(decayed_plant)
        
    return updated_plants

@app.post("/plant/action")
def perform_plant_action(action_data: PlantActionSchema):
    """Perform an action (water, feed, fertilize) on a plant."""
    plant = db_client.get_plant_by_id(action_data.plant_id)
    
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found.")
    
    # 1. Apply Decay first to get the current true state 
    decayed_plant = apply_decay(plant)

    # 2. Apply the user action to the decayed state
    updated_plant, message = apply_action(decayed_plant, action_data.action_type)
    
    # 3. Persist the new state to the database
    # The action function returns the plant with updated derived stats
    success = db_client.update_plant_state(updated_plant['plant_id'], updated_plant)

    if success:
        # Add derived stats for the frontend response
        level, xp_needed = calculate_level_xp(updated_plant['xp'])
        updated_plant['level'] = level
        updated_plant['xp_needed'] = xp_needed
        updated_plant['mood'] = get_plant_mood(updated_plant['health'])
        
        # 4. Log the interaction
        # We log the actual health gain from the action, excluding decay
        health_effect = updated_plant['health'] - decayed_plant['health']
        db_client.log_interaction(
            updated_plant['plant_id'],
            action_data.action_type,
            health_effect
        )

        return {"message": message, "plant_state": updated_plant}
    
    raise HTTPException(status_code=500, detail="Failed to update plant state after action.")

@app.get("/plant/{plant_id}/history")
def get_plant_history(plant_id: int):
    """Retrieve interaction history for a specific plant."""
    history = db_client.get_interaction_history(plant_id)
    if not history:
        return []
    
    # Convert 'effect_value' from string (if stored as one) to integer
    for item in history:
        try:
            item['effect_value'] = int(item['effect_value'])
        except (ValueError, TypeError):
            item['effect_value'] = 0 # Default to 0 if data is bad
            
    return history
