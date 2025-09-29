import os
from supabase import create_client, Client
from typing import List, Dict, Any, Optional

class SupabaseDB:
    """A client class to handle all interactions with the Supabase database."""
    def __init__(self, url: str, key: str):
        # Initialize Supabase client
        self.supabase: Client = create_client(url, key)
        self.db = self.supabase.table # Use the table client for simplicity

    # --- User Operations ---

    def create_user(self, username: str, email: str) -> Optional[Dict[str, Any]]:
        """Creates a new user and returns the user data."""
        try:
            # Insert operation
            response = self.db('users').insert({"username": username, "email": email}).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            # Log the error (optional in deployment, good for debugging)
            # print(f"Error creating user: {e}") 
            return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieves a user by username."""
        # Select operation, checking for equality
        response = self.db('users').select("*").eq('username', username).execute()
        if response.data:
            return response.data[0]
        return None

    # --- Plant Operations ---

    def create_plant(self, user_id: int, plant_name: str, level: int, xp: int, health: int, soil_quality: int, mood: str) -> Optional[Dict[str, Any]]:
        """Creates a new plant for a given user."""
        try:
            data = {
                "user_id": user_id,
                "plant_name": plant_name,
                "level": level,
                "xp": xp,
                "health": health,
                "soil_quality": soil_quality,
            }
            response = self.db('plants').insert(data).execute()
            if response.data:
                # Add mood for consistency, though it's not stored in the DB
                response.data[0]['mood'] = mood 
                return response.data[0]
            return None
        except Exception as e:
            # print(f"Error creating plant: {e}")
            return None
            
    def get_plant_by_id(self, plant_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single plant by its ID."""
        response = self.db('plants').select("*").eq('plant_id', plant_id).execute()
        if response.data:
            return response.data[0]
        return None

    def get_plants_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieves all plants belonging to a user."""
        response = self.db('plants').select("*").eq('user_id', user_id).execute()
        return response.data if response.data else []
        
    def update_plant_state(self, plant_id: int, plant_data: Dict[str, Any]) -> bool:
        """Updates the core state fields (health, xp, soil, last_updated) of a plant."""
        try:
            # Filter the dictionary to only include fields we want to update/store
            update_data = {
                'health': plant_data['health'],
                'xp': plant_data['xp'],
                'soil_quality': plant_data['soil_quality'],
                'last_updated': plant_data['last_updated'] # Crucial for decay
            }
            # Perform the update
            self.db('plants').update(update_data).eq('plant_id', plant_id).execute()
            return True
        except Exception as e:
            # print(f"Error updating plant state: {e}")
            return False

    # --- Interaction History ---

    def log_interaction(self, plant_id: int, action_type: str, effect_value: int) -> bool:
        """Logs a user interaction or dynamic event."""
        try:
            data = {
                "plant_id": plant_id,
                "action_type": action_type,
                "effect_value": effect_value
            }
            self.db('interactions').insert(data).execute()
            return True
        except Exception as e:
            # print(f"Error logging interaction: {e}")
            return False

    def get_interaction_history(self, plant_id: int) -> List[Dict[str, Any]]:
        """Retrieves the history of interactions for a plant, ordered by time."""
        response = self.db('interactions').select("*").eq('plant_id', plant_id).order('created_at', desc=True).limit(20).execute()
        return response.data if response.data else []
