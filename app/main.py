import streamlit as st
from ui_components import render_travel_form
from itinerary_dashboard import render_itinerary_dashboard

def main():
    st.set_page_config(
        page_title="AI Travel Planner",
        page_icon="✈️",
        layout="wide"
    )
    
    st.title("AI-Powered Travel Planner")
    st.write("Create personalized travel itineraries with AI assistance")
    
    # Initialize session state
    if 'itinerary' not in st.session_state:
        st.session_state.itinerary = None
    
    # Render the main interface
    render_travel_form()
    
    if st.session_state.itinerary:
        render_itinerary_dashboard(st.session_state.itinerary)

if __name__ == "__main__":
    main() 