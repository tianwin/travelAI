import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def render_itinerary_dashboard(itinerary_data):
    st.header("Your Travel Itinerary")
    
    # Display trip summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Destination", itinerary_data["destination"])
    with col2:
        st.metric("Duration", f"{itinerary_data['duration']} days")
    with col3:
        st.metric("Budget", f"${itinerary_data['budget']}")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Day-by-Day", "Map View", "Budget Breakdown"])
    
    with tab1:
        render_day_by_day_view(itinerary_data)
    
    with tab2:
        st.write("Map view coming soon...")
        # TODO: Implement map visualization
    
    with tab3:
        render_budget_breakdown(itinerary_data)

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