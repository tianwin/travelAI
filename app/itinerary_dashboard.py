import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def render_itinerary_dashboard(itinerary):
    """Render the itinerary dashboard with day selection and activity details."""
    # Initialize session state for selected day if not exists
    if 'selected_day' not in st.session_state:
        st.session_state.selected_day = 1
    
    # Create day selection dropdown
    days = [f"Day {day['day_number']}" for day in itinerary['days']]
    selected_day_index = st.session_state.selected_day - 1
    
    # Update selected day if dropdown changes
    new_selection = st.selectbox(
        "Select Day",
        options=days,
        index=selected_day_index,
        key="day_selector"
    )
    
    # Update session state with new selection
    st.session_state.selected_day = int(new_selection.split()[-1])
    
    # Get the selected day's activities
    selected_day = next(day for day in itinerary['days'] if day['day_number'] == st.session_state.selected_day)
    
    # Display day summary
    st.subheader(f"Day {st.session_state.selected_day}")
    
    # Create a DataFrame for the selected day's activities
    activities_data = []
    for activity in selected_day['activities']:
        activities_data.append({
            'Time': activity['time'],
            'Activity': activity['title'],
            'Duration': activity['duration'],
            'Cost': f"${activity['cost']}",
            'Location': activity['location'],
            'Transportation': activity['transportation']
        })
    
    df = pd.DataFrame(activities_data)
    
    # Display activities in a table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Time": st.column_config.TextColumn(
                "Time",
                width="small",
            ),
            "Activity": st.column_config.TextColumn(
                "Activity",
                width="medium",
            ),
            "Duration": st.column_config.TextColumn(
                "Duration",
                width="small",
            ),
            "Cost": st.column_config.TextColumn(
                "Cost",
                width="small",
            ),
            "Location": st.column_config.TextColumn(
                "Location",
                width="medium",
            ),
            "Transportation": st.column_config.TextColumn(
                "Transportation",
                width="medium",
            ),
        }
    )
    
    # Display detailed descriptions for each activity
    st.subheader("Activity Details")
    for activity in selected_day['activities']:
        with st.expander(f"{activity['time']} - {activity['title']}"):
            # Create columns for better layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Render markdown in the description with proper spacing
                st.markdown(activity['description'])
                st.markdown("---")
            
            with col2:
                # Display additional details in a structured format
                st.markdown("**Quick Info:**")
                st.markdown(f"📍 **Location:**\n`{activity['location']}`")
                st.markdown(f"🚗 **Transportation:**\n{activity['transportation']}")
                st.markdown(f"⏱️ **Duration:**\n{activity['duration']}")
                st.markdown(f"💰 **Cost:**\n${activity['cost']}")
    
    # Display trip summary with better formatting
    with st.expander("Trip Summary"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Trip Details:**")
            st.markdown(f"🌍 **Destination:**\n{itinerary['destination'].title()}")
            st.markdown(f"📅 **Duration:**\n{itinerary['duration']} days")
            st.markdown(f"💵 **Budget:**\n${itinerary['budget']}")
        
        with col2:
            st.markdown("**Preferences:**")
            st.markdown(f"🎯 **Travel Style:**\n{itinerary['travel_style']}")
            st.markdown(f"❤️ **Interests:**\n{', '.join(itinerary['interests'])}")
        
        # Calculate and display costs
        total_cost = sum(
            activity['cost']
            for day in itinerary['days']
            for activity in day['activities']
        )
        remaining_budget = itinerary['budget'] - total_cost
        
        st.markdown("---")
        st.markdown("**Budget Summary:**")
        st.markdown(f"💰 **Total Estimated Cost:**\n${total_cost}")
        st.markdown(f"💵 **Remaining Budget:**\n${remaining_budget}")

def render_day_by_day_view(itinerary_data):
    for day_data in itinerary_data.get("days", []):
        day_number = day_data.get("day_number", 0)
        activities = day_data.get("activities", [])
        
        with st.expander(f"Day {day_number}", expanded=True):
            if not activities:
                st.info("No activities planned for this day.")
                continue
                
            for activity in activities:
                with st.container():
                    st.subheader(f"{activity['time']} - {activity['title']}")
                    
                    # Activity details in columns
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(activity['description'])
                        st.write(f"📍 **Location:** {activity['location']}")
                        if activity.get('transportation'):
                            st.write(f"🚗 **Transportation:** {activity['transportation']}")
                    
                    with col2:
                        st.write(f"⏱️ **Duration:** {activity['duration']}")
                        st.write(f"💰 **Cost:** ${activity['cost']}")
                    
                    st.divider()

def render_budget_breakdown(itinerary_data):
    # Calculate total costs from activities
    total_costs = {
        "Activities": sum(activity['cost'] for day in itinerary_data.get("days", []) 
                         for activity in day.get("activities", [])),
        "Accommodation": itinerary_data.get("budget", 0) * 0.4,  # Estimated 40% for accommodation
        "Food": itinerary_data.get("budget", 0) * 0.2,  # Estimated 20% for food
        "Transportation": itinerary_data.get("budget", 0) * 0.2,  # Estimated 20% for transportation
        "Miscellaneous": itinerary_data.get("budget", 0) * 0.2  # Estimated 20% for miscellaneous
    }
    
    # Create DataFrame for visualization
    df = pd.DataFrame({
        "Category": list(total_costs.keys()),
        "Amount": list(total_costs.values())
    })
    
    # Display budget breakdown
    st.subheader("Budget Breakdown")
    st.bar_chart(df.set_index("Category"))
    
    # Display total cost
    total_cost = sum(total_costs.values())
    st.metric("Total Estimated Cost", f"${total_cost:,.2f}") 