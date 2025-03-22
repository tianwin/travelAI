import streamlit as st
from datetime import datetime, timedelta
from agents.itinerary_agent import ItineraryAgent
import yaml
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def render_travel_form():
    with st.form("travel_planning_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            destination = st.text_input("Destination", placeholder="e.g., London, Paris")
            start_date = st.date_input("Start Date", min_value=datetime.now().date())
            duration = st.number_input("Duration (days)", min_value=1, max_value=30, value=3)
            
        with col2:
            budget = st.number_input("Budget ($)", min_value=100, max_value=10000, value=1000)
            travel_style = st.selectbox(
                "Travel Style",
                ["Luxury", "Comfort", "Budget", "Adventure", "Cultural"]
            )
            interests = st.multiselect(
                "Interests",
                ["History", "Food", "Nature", "Art", "Shopping", "Nightlife"]
            )
        
        submitted = st.form_submit_button("Generate Itinerary")
        
        if submitted:
            try:
                # Load configuration
                config = load_config()
                
                # Initialize the agent
                agent = ItineraryAgent(api_key=config['api_keys']['groq'])
                
                # Prepare preferences
                preferences = {
                    "destination": destination,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "duration": duration,
                    "budget": budget,
                    "travel_style": travel_style,
                    "interests": interests
                }
                
                # Generate itinerary
                with st.spinner("Generating your personalized itinerary..."):
                    itinerary = agent.generate_itinerary(preferences)
                    st.session_state.itinerary = itinerary
            except Exception as e:
                st.error(f"Failed to generate itinerary: {str(e)}")
                st.session_state.itinerary = None 