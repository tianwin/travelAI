import streamlit as st
from datetime import datetime, timedelta

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
            # TODO: Call itinerary generation logic
            st.session_state.itinerary = {
                "destination": destination,
                "start_date": start_date,
                "duration": duration,
                "budget": budget,
                "travel_style": travel_style,
                "interests": interests
            } 