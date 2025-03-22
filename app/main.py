import streamlit as st
from ui_components import render_travel_form
from itinerary_dashboard import render_itinerary_dashboard
from chat_interface import render_chat_interface

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
    
    # Create two columns: chat on the left, itinerary on the right
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        st.subheader("Chat with AI Assistant")
        render_chat_interface()
    
    with right_col:
        st.subheader("Your Itinerary")
        if st.session_state.itinerary:
            render_itinerary_dashboard(st.session_state.itinerary)
        else:
            render_travel_form()

if __name__ == "__main__":
    main() 