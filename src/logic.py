import math
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

# --- Constants for Game Balance ---
XP_PER_LEVEL = 100
MAX_STAT = 100

# Decay rates per hour of neglect
DECAY_RATE_HEALTH_PER_HOUR = 2  # 2% health decay per hour
DECAY_RATE_SOIL_PER_HOUR = 0.5 # 0.5% soil quality decay per hour

# Action effects
ACTION_EFFECTS = {
    "water": {"health": 15, "xp": 5, "soil_quality": 0},
    "feed": {"health": 10, "xp": 10, "soil_quality": 5},
    "fertilize": {"health": 20, "xp": 15, "soil_quality": 10},
    "rain": {"health": 25, "xp": 5, "soil_quality": 0}, # Placeholder for future dynamic event
}

# --- Utility Functions ---

def _clamp(value: float, min_val: float = 0, max_val: float = MAX_STAT) -> int:
    """Clamps a value to be within the min and max range."""
    return int(max(min_val, min(max_val, value)))

def calculate_time_difference(last_updated_str: str) -> Tuple[float, datetime]:
    """Calculates the time elapsed in hours since the last update."""
    
    # Supabase returns ISO 8601 strings, often with 'Z' for UTC
    last_updated = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))

    # Ensure the datetime object is timezone-aware and converted to UTC
    if last_updated.tzinfo is None or last_updated.tzinfo.utcoffset(last_updated) is None:
        last_updated = last_updated.replace(tzinfo=timezone.utc)
    
    now_utc = datetime.now(timezone.utc)
    
    time_diff = now_utc - last_updated
    hours_elapsed = time_diff.total_seconds() / 3600.0
    
    # Return hours elapsed and the current time (to be used as the new 'last_updated')
    return hours_elapsed, now_utc

# --- Core Logic Functions ---

def get_plant_mood(health: int) -> str:
    """Determines the plant's mood based on its health."""
    if health >= 80:
        return "😊 Happy"
    elif health >= 50:
        return "😐 Neutral"
    elif health >= 20:
        return "😟 Needs Care"
    else:
        return "😢 Critical"

def calculate_level_xp(current_xp: int) -> Tuple[int, int]:
    """Calculates level and XP needed for the next level."""
    level = 1 + (current_xp // XP_PER_LEVEL)
    xp_needed_for_next_level = XP_PER_LEVEL - (current_xp % XP_PER_LEVEL)
    return level, xp_needed_for_next_level

def apply_decay(plant: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies health decay based on the time since the last update (neglect).
    Returns the updated plant data.
    """
    hours_elapsed, new_timestamp = calculate_time_difference(plant['last_updated'])

    if hours_elapsed > 0:
        # 1. Calculate Decay
        health_decay = hours_elapsed * DECAY_RATE_HEALTH_PER_HOUR
        soil_decay = hours_elapsed * DECAY_RATE_SOIL_PER_HOUR
        
        # 2. Apply Decay (Decay should not increase health/soil)
        new_health = plant['health'] - health_decay
        new_soil = plant['soil_quality'] - soil_decay
        
        # 3. Clamp values and update timestamp
        plant['health'] = _clamp(new_health)
        plant['soil_quality'] = _clamp(new_soil)
        # Update the timestamp using the standard ISO format
        plant['last_updated'] = new_timestamp.isoformat().replace('+00:00', 'Z')
        
        # 4. Update derived properties for response/storage
        plant['mood'] = get_plant_mood(plant['health'])
        plant['level'], plant['xp_needed'] = calculate_level_xp(plant['xp'])

    return plant

def apply_action(plant: Dict[str, Any], action_type: str) -> Tuple[Dict[str, Any], str]:
    """
    Applies the effects of an action to the plant's stats.
    Assumes decay has already been applied by the API caller.
    """
    effects = ACTION_EFFECTS.get(action_type, {"health": 0, "xp": 0, "soil_quality": 0})
    
    # Soil quality modifies the effectiveness of the action (e.g., poor soil reduces benefit)
    # Factor is 0.5 (for 0% soil) up to 1.5 (for 100% soil)
    effectiveness_factor = 0.5 + (plant['soil_quality'] / 200.0) 

    # 1. Calculate New Stats
    health_boost = effects['health'] * effectiveness_factor
    xp_boost = effects['xp']
    soil_boost = effects['soil_quality']

    # 2. Update Stats
    plant['health'] = _clamp(plant['health'] + health_boost)
    plant['xp'] += xp_boost
    plant['soil_quality'] = _clamp(plant['soil_quality'] + soil_boost)
    
    # 3. Recalculate derived properties
    plant['mood'] = get_plant_mood(plant['health'])
    plant['level'], plant['xp_needed'] = calculate_level_xp(plant['xp'])
    plant['last_updated'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    message = f"Applied {action_type}! Health gained {int(health_boost)}, XP gained {xp_boost}."
    
    return plant, message
