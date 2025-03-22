import streamlit as st
from agents.chat_agent import ChatAgent
import yaml
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def initialize_chat():
    """Initialize chat session state."""
    if 'chat_agent' not in st.session_state:
        config = load_config()
        st.session_state.chat_agent = ChatAgent(api_key=config['api_keys']['groq'])
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'pending_modification' not in st.session_state:
        st.session_state.pending_modification = None

def render_chat_interface():
    """Render the chat interface."""
    initialize_chat()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your itinerary or request modifications..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get current itinerary from session state
        current_itinerary = st.session_state.get('itinerary')
        
        try:
            # Process the message
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chat_agent.process_message(
                        prompt,
                        current_itinerary
                    )
                    
                    # Display the response
                    st.write(response["message"])
                    
                    # Check for itinerary modifications
                    if response.get("modified_itinerary") and response["modified_itinerary"] != current_itinerary:
                        st.session_state.pending_modification = response["modified_itinerary"]
                        st.warning("I've suggested some modifications to your itinerary. Would you like to apply these changes?")
                        
                        # Show the differences
                        if current_itinerary:
                            st.write("Changes to be made:")
                            for day in response["modified_itinerary"]["days"]:
                                day_num = day["day_number"]
                                current_day = next((d for d in current_itinerary["days"] if d["day_number"] == day_num), None)
                                
                                if current_day:
                                    st.write(f"\nDay {day_num}:")
                                    for activity in day["activities"]:
                                        current_activity = next((a for a in current_day["activities"] if a["time"] == activity["time"]), None)
                                        if not current_activity or current_activity != activity:
                                            st.write(f"- {activity['time']}: {activity['title']}")
                        
                        # Confirmation buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Apply Changes", key="apply_changes"):
                                st.session_state.itinerary = st.session_state.pending_modification
                                st.session_state.pending_modification = None
                                st.success("Itinerary has been updated!")
                                st.rerun()
                        
                        with col2:
                            if st.button("Keep Original", key="keep_original"):
                                st.session_state.pending_modification = None
                                st.info("Keeping original itinerary")
                                st.rerun()
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response["message"]})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I encountered an error: {str(e)}"})
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_agent.clear_history()
        st.session_state.pending_modification = None
        st.rerun() 