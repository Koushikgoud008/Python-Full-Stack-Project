import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any 
from streamlit.components.v1 import html # Required for robust HTML/SVG rendering

# --- Configuration ---
# NOTE: If running FastAPI locally, ensure this URL is correct.
API_BASE_URL = "http://localhost:8000"

# --- State Management Keys ---
USER_KEY = 'current_user'
PLANT_KEY = 'selected_plant'

# --- Custom Styling ---

def apply_custom_styles():
    """Injects custom CSS for a modern, attractive theme with animations."""
    st.markdown("""
        <style>
        /* Overall App Theme and Font */
        .stApp {
            background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 100%);
            color: #064e3b; /* Darker, more visible text for high contrast */
            font-family: 'Inter', sans-serif;
        }
        /* Sidebar Styling */
        .st-emotion-cache-1cypcdb {
            background-color: #a7f3d0;
            border-right: 2px solid #34d399;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        /* Headers - Ensuring high visibility */
        h1, h2, h3 {
            color: #065f46;
            text-shadow: 1px 1px 2px #c9f5e2; 
        }
        /* Buttons Styling (Interactive look) */
        .stButton>button {
            background-color: #34d399; /* Green base */
            color: white;
            border-radius: 10px;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.2);
            transition: all 0.2s;
        }
        .stButton>button:hover {
            background-color: #059669; /* Darker green on hover */
            box-shadow: 5px 5px 8px rgba(0, 0, 0, 0.3);
            transform: translateY(-2px);
        }
        /* Metric Cards (Styled containers for Level/XP/Mood) */
        .metric-card {
            background-color: white;
            padding: 15px;
            border-radius: 15px;
            box-shadow: 5px 5px 15px rgba(167, 243, 208, 0.8);
            border-left: 5px solid #10b981;
            margin-bottom: 20px;
            transition: transform 0.3s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }

        /* --- Dynamic Plant Animation CSS --- */

        /* Animation Keyframes */
        @keyframes sway {
            0% { transform: rotate(0deg); }
            50% { transform: rotate(2deg); }
            100% { transform: rotate(-2deg); }
        }
        
        /* Base Plant Visual Container */
        .plant-visual-container {
            text-align: center;
            margin: 30px auto;
            max-width: 200px;
            cursor: pointer; /* Indicate interactivity */
        }
        
        /* Plant SVG Base Style */
        .plant-visual {
            width: 150px;
            height: 150px;
            transition: all 0.5s ease;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
        }

        /* Wind Effect on Hover */
        .plant-visual-container:hover .plant-visual {
            animation: sway 0.3s ease-in-out infinite alternate;
        }

        /* Dynamic Health Effects (Grayscale/Opacity = Less Greenery) */
        
        /* Health >= 80: Full color, vibrant */
        .health-high {
            filter: grayscale(0%) opacity(1);
        }
        
        /* Health 50-79: Slight desaturation */
        .health-medium {
            filter: grayscale(5%) opacity(0.95);
        }
        
        /* Health 20-49: Noticeable desaturation and reduced vitality */
        .health-low {
            filter: grayscale(20%) opacity(0.85);
        }
        
        /* Health < 20: Critical, significant wilting look */
        .health-critical {
            filter: grayscale(50%) opacity(0.7);
            transform: scale(0.95) translateY(5px);
        }
        
        /* Stop sway animation when plant is critical */
        .health-critical:hover {
            animation: none;
        }
        </style>
        """, unsafe_allow_html=True)


# --- Utility Functions ---

def api_request(method: str, endpoint: str, data: dict = None):
    """General function to handle API calls."""
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: Could not connect or failed to process request. Ensure FastAPI is running on {API_BASE_URL}.")
        # st.exception(e) # Removed exception display to keep UI clean unless debugging
        return None

def get_health_class(health: int) -> str:
    """Returns a CSS class string based on plant health for dynamic styling."""
    if health >= 80:
        return "health-high"
    elif health >= 50:
        return "health-medium"
    elif health >= 20:
        return "health-low"
    else:
        return "health-critical"

# NEW HELPER: Isolates the large SVG markup for robust rendering via HTML component
def _render_dynamic_plant_svg(health: int, health_class: str):
    """Renders the dynamic SVG plant visual using the streamlit.components.v1.html component."""
    
    # Use a simplified SVG structure to avoid deep rendering issues
    plant_html = f"""
        <div class="plant-visual-container" title="Current Health: {health}%">
            <svg class="plant-visual {health_class}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                
                <!-- Stem -->
                <rect x="11.5" y="4" width="1" height="13" rx="0.5" fill="#059669"/>
                
                <!-- Main Canopy (Leaves) -->
                <path 
                    d="M12 4C10 4 8 6 8 8C8 10 10 12 12 12C14 12 16 10 16 8C16 6 14 4 12 4Z" 
                    fill="#34D399" 
                    stroke="#065F46" 
                    stroke-width="1" 
                    stroke-linecap="round" 
                    stroke-linejoin="round"/>
                
                <!-- Side Leaf 1 -->
                <path d="M16 10L19 7" stroke="#065F46" stroke-width="1" stroke-linecap="round"/>
                <path d="M19 7C19.5 7 20 7.5 20 8L17 11C16.5 11.5 16 11.5 16 11L16 10Z" fill="#34D399" stroke="#065F46" stroke-width="1" stroke-linejoin="round"/>
                
                <!-- Side Leaf 2 -->
                <path d="M8 10L5 7" stroke="#065F46" stroke-width="1" stroke-linecap="round"/>
                <path d="M5 7C4.5 7 4 7.5 4 8L7 11C7.5 11.5 8 11.5 8 11L8 10Z" fill="#34D399" stroke="#065F46" stroke-width="1" stroke-linejoin="round"/>
                
                <!-- Pot -->
                <rect x="6" y="17" width="12" height="4" rx="2" fill="#A8A29E" stroke="#78716C" stroke-width="1"/>
                
                <!-- Soil line -->
                <path d="M6 17H18" stroke="#78716C" stroke-width="1.5" stroke-linecap="round"/>

            </svg>
        </div>
    """
    
    # Render the HTML inside an isolated iframe (the most robust method)
    with st.container():
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        html(plant_html, height=250, scrolling=False) 
        st.markdown("</div>", unsafe_allow_html=True)


# --- Draw Functions ---

def draw_health_bar(health: int, label: str):
    """Draws a custom, attractive progress bar with a gradient and shadow."""
    st.markdown(f"<p style='font-weight: 600; color: #047857; margin-bottom: 5px;'>{label}: {health}%</p>", unsafe_allow_html=True)
    
    # Define colors for gradient based on health
    if health > 80:
        color_start, color_end = "#10b981", "#059669" # High Health: Emerald
    elif health > 50:
        color_start, color_end = "#facc15", "#fbbf24" # Mid Health: Yellow/Amber
    elif health > 20:
        color_start, color_end = "#f97316", "#ea580c" # Low Health: Orange
    else:
        color_start, color_end = "#ef4444", "#b91c1c" # Critical Health: Red

    st.markdown(
        f"""
        <div style='background-color: #d1fae5; border-radius: 12px; height: 20px; margin-bottom: 20px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);'>
            <div style='
                background: linear-gradient(90deg, {color_start}, {color_end});
                height: 100%; 
                width: {health}%; 
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                transition: width 0.5s ease;
            '>
            </div>
        </div>
        """, unsafe_allow_html=True
    )

def draw_history_chart(history_data: List[Dict[str, Any]], plant_name: str):
    """Generates a simple plot of interaction values over time."""
    if not history_data:
        st.info("No interaction history yet.")
        return

    # Convert to DataFrame for easy manipulation
    df = pd.DataFrame(history_data)
    
    # Sort by time
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values('created_at', ascending=True)

    # Prepare data for plotting
    df['cumulative_effect'] = df['effect_value'].cumsum()
    df['action_label'] = df['action_type'] + ' (' + df['effect_value'].astype(str) + ')'

    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plot cumulative effect
    ax.plot(df['created_at'], df['cumulative_effect'], marker='o', linestyle='-', color='#047857', label='Cumulative Effect') # Use darker green for plot
    
    # Add scatter points for individual events
    for i, row in df.iterrows():
        # Corrected column name to 'effect_value'
        color = '#10b981' if row['effect_value'] > 0 else '#ef4444'
        ax.scatter(row['created_at'], row['cumulative_effect'], color=color, zorder=5)

    ax.set_title(f"Growth History for {plant_name}", fontsize=16)
    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("Cumulative Score/XP", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    st.pyplot(fig)


# --- Main UI Components ---

def login_ui():
    """Handles user login/registration."""
    st.header("Welcome to PlantCare XP! 🌱")
    
    username = st.text_input("Enter your Username to load your profile or register:")
    email = st.text_input("Enter your Email (for new users only):")

    if st.button("Access/Register PlantCare"):
        if not username:
            st.warning("Please enter a username.")
            return

        user_data = api_request("POST", "users/register", {"username": username, "email": email or f"{username}@plantcare.com"})
        
        if user_data and user_data.get('user'):
            st.session_state[USER_KEY] = user_data['user']
            st.success(user_data['message'])
            st.rerun()

def plant_dashboard_ui():
    """Main dashboard for viewing and interacting with the selected plant."""
    user = st.session_state[USER_KEY]
    st.sidebar.title(f"Hello, {user['username']}!")
    
    # 1. Fetch user's plants
    plants_data = api_request("GET", f"plants/{user['user_id']}")

    if not plants_data:
        st.subheader("No Plants Yet!")
        plant_creation_ui(user['user_id'])
        return

    # 2. Plant Selection
    plant_names = {p['plant_name']: p for p in plants_data}
    selected_name = st.sidebar.selectbox("Select Your Plant:", list(plant_names.keys()))
    
    # Store the currently selected plant in session state
    st.session_state[PLANT_KEY] = plant_names[selected_name]
    current_plant = st.session_state[PLANT_KEY]
    
    # --- Plant Status Display (Enhanced Metrics) ---
    st.title(f"💚 Monitoring: {current_plant['plant_name']}")
    
    col1, col2, col3 = st.columns(3)
    
    # Card 1: Level
    col1.markdown(f"""
        <div class="metric-card">
            <p style="font-size: 14px; color: #4b5563; margin: 0;">🌳 Level</p>
            <h3 style="color: #047857; margin: 5px 0 0 0; font-size: 32px;">{current_plant['level']}</h3>
        </div>
    """, unsafe_allow_html=True)

    # Card 2: XP
    xp_text = f"{current_plant['xp']}/{current_plant['xp'] + current_plant['xp_needed']}"
    col2.markdown(f"""
        <div class="metric-card">
            <p style="font-size: 14px; color: #4b5563; margin: 0;">✨ XP Progress</p>
            <h3 style="color: #f59e0b; margin: 5px 0 0 0; font-size: 32px;">{xp_text}</h3>
        </div>
    """, unsafe_allow_html=True)

    # Card 3: Mood
    mood_emoji = current_plant['mood'].split()[0]
    col3.markdown(f"""
        <div class="metric-card">
            <p style="font-size: 14px; color: #4b5563; margin: 0;">🌱 Mood</p>
            <h3 style="color: #6366f1; margin: 5px 0 0 0; font-size: 32px;">{mood_emoji}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # --- Dynamic Plant Visual (New Section with SVG and Animation) ---
    
    # Get CSS class based on health
    health_class = get_health_class(current_plant['health'])
    
    # CRITICAL FIX: Calling the isolated rendering function
    _render_dynamic_plant_svg(current_plant['health'], health_class)

    # Health and Soil Bars
    draw_health_bar(current_plant['health'], "Health")
    draw_health_bar(current_plant['soil_quality'], "Soil Quality")

    # --- Interaction Section ---
    st.subheader("Take Action")
    
    action = st.radio(
        "Choose an action to improve your plant's health:",
        ('water', 'feed', 'fertilize'),
        horizontal=True
    )
    
    # The button will now be styled by the injected CSS
    if st.button(f"Perform {action.capitalize()} Action"):
        perform_action_and_update(current_plant['plant_id'], action)
    
    # --- Reports & Insights ---
    st.subheader("Growth History")
    history = api_request("GET", f"plant/{current_plant['plant_id']}/history")
    
    if history:
        draw_history_chart(history, current_plant['plant_name'])
        
    st.sidebar.divider()
    plant_creation_ui(user['user_id'], is_sidebar=True)

def plant_creation_ui(user_id: int, is_sidebar: bool = False):
    """UI for creating a new plant."""
    if is_sidebar:
        st.sidebar.subheader("New Plant")
        plant_name_input = st.sidebar.text_input("Name your new plant:")
        create_button = st.sidebar.button("Adopt New Plant")
    else:
        st.subheader("Adopt a New Plant")
        plant_name_input = st.text_input("Name your new plant:")
        create_button = st.button("Adopt New Plant")

    if create_button and plant_name_input:
        with st.spinner(f"Creating plant '{plant_name_input}'..."):
            plant_data = api_request("POST", "plants/create", {
                "user_id": user_id,
                "plant_name": plant_name_input
            })
        
        if plant_data:
            st.success(f"Plant '{plant_data['plant_name']}' adopted successfully!")
            st.rerun()
        else:
            st.error("Failed to adopt plant.")


def perform_action_and_update(plant_id: int, action_type: str):
    """Calls the action API and updates the UI state."""
    with st.spinner(f"Applying '{action_type}' to plant..."):
        result = api_request("POST", "plant/action", {
            "plant_id": plant_id,
            "action_type": action_type
        })

    if result:
        st.success(result['message'])
        # Update the session state with the new plant state from the API response
        st.session_state[PLANT_KEY] = result['plant_state']
        st.rerun() # Rerun to refresh the dashboard
    else:
        st.error("Action failed.")

# --- Application Entry Point ---

def main():
    st.set_page_config(
        page_title="PlantCare XP", 
        layout="wide", 
        initial_sidebar_state="expanded"
    )
    
    apply_custom_styles() # <-- Added to inject attractive CSS
    st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)

    # Check for API connection health before proceeding
    if api_request("GET", "") is None:
        st.error("Cannot connect to the FastAPI backend. Please ensure it is running.")
        return

    # Routing based on session state
    if USER_KEY not in st.session_state:
        login_ui()
    else:
        plant_dashboard_ui()

if __name__ == "__main__":
    main()
