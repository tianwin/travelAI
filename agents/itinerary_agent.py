from typing import Dict, List, Optional
import groq
import json
import yaml
import os
from datetime import datetime
from .markdown_templates import format_activity_description, format_itinerary_summary, format_day_summary

class ItineraryAgent:
    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0.7, max_tokens: int = 4000):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = groq.Groq(api_key=api_key)
        print("🤖 ItineraryAgent initialized with Groq client")
    
    def generate_itinerary(self, preferences: Dict) -> Dict:
        """
        Generate a travel itinerary based on user preferences.
        
        Args:
            preferences (Dict): User's travel preferences
            
        Returns:
            Dict: Generated itinerary
        """
        try:
            # Prepare the system message with a pre-formatted example
            system_message = """You are a travel planning assistant. Generate a detailed travel itinerary based on the user's preferences.
            
            The itinerary should be returned as a JSON object with the following structure:
            {
                "days": [
                    {
                        "day_number": 1,
                        "activities": [
                            {
                                "time": "09:00",
                                "title": "Activity Name",
                                "description": "**Activity Name**\n\nStart your day with a visit to **Buckingham Palace**, the official residence of the British monarch.\n\n*Important Tips:*\n- Book tickets in advance\n- Arrive 15 minutes early\n- Photography not allowed inside\n\n*Important Notes:*\n> The Changing of the Guard ceremony takes place at 11:00 AM\n\n**Location Details:**\n- Address: `Buckingham Palace, London SW1A 1AA`\n- Nearest Tube: `Green Park Station`\n\n**Getting There:**\nTake the Tube to Green Park Station, then walk 5 minutes",
                                "duration": "2 hours",
                                "cost": 30,
                                "location": "Buckingham Palace, London SW1A 1AA",
                                "transportation": "Take the Tube to Green Park Station, then walk 5 minutes"
                            }
                        ]
                    }
                ]
            }
            
            Guidelines for the itinerary:
            1. Each day should have 3-5 activities
            2. Activities should be spaced throughout the day
            3. Include transportation details between activities
            4. Provide realistic costs for each activity
            5. Use markdown formatting in descriptions for better readability
            6. Include tips and important notes for each activity
            7. Consider the user's budget and preferences
            8. Include a mix of popular attractions and local experiences
            
            The itinerary should be well-structured and provide a good balance of activities while staying within the user's budget."""
            
            # Prepare the user message
            user_message = f"""Please generate a travel itinerary based on these preferences:
            {json.dumps(preferences, indent=2)}"""
            
            # Call Groq API
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Get the response
            response_text = completion.choices[0].message.content
            
            # Extract the itinerary from the response
            itinerary = self._extract_itinerary(response_text, preferences)
            
            if itinerary:
                # Add summary information
                itinerary["summary"] = self._generate_summary(itinerary, preferences)
                return itinerary
            else:
                raise Exception("Failed to generate a valid itinerary")
            
        except Exception as e:
            print(f"Error generating itinerary: {str(e)}")
            raise
    
    def _extract_itinerary(self, response_text: str, preferences: Dict) -> Optional[Dict]:
        """Extract the itinerary from the response text."""
        try:
            # Look for JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                
                # Clean the JSON string
                # Remove any control characters
                json_str = ''.join(char for char in json_str if ord(char) >= 32 or char in '\n\r\t')
                # Replace any non-printable characters with spaces
                json_str = ''.join(char if char.isprintable() else ' ' for char in json_str)
                # Remove any extra whitespace
                json_str = ' '.join(json_str.split())
                
                # Handle newlines in markdown text
                json_str = json_str.replace('\n', '\\n')
                
                try:
                    itinerary_data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {str(e)}")
                    print("Cleaned JSON string:")
                    print(json_str)
                    return None
                
                # Validate the structure
                if not isinstance(itinerary_data, dict):
                    print("Error: Response is not a dictionary")
                    return None
                
                if "days" not in itinerary_data:
                    print("Error: Response missing 'days' key")
                    return None
                
                if not isinstance(itinerary_data["days"], list):
                    print("Error: 'days' is not a list")
                    return None
                
                # Validate each day has required fields
                for day in itinerary_data["days"]:
                    if not isinstance(day, dict):
                        print("Error: Day is not a dictionary")
                        return None
                    
                    if "day_number" not in day:
                        print("Error: Day missing 'day_number'")
                        return None
                    
                    if "activities" not in day:
                        print("Error: Day missing 'activities'")
                        return None
                    
                    if not isinstance(day["activities"], list):
                        print("Error: Activities is not a list")
                        return None
                    
                    # Validate each activity has required fields
                    for activity in day["activities"]:
                        required_fields = ["time", "title", "description", "duration", "cost", "location", "transportation"]
                        for field in required_fields:
                            if field not in activity:
                                print(f"Error: Activity missing '{field}'")
                                return None
                
                # Add metadata from preferences
                itinerary_data.update({
                    "destination": preferences.get("destination", "Unknown Destination"),
                    "start_date": preferences.get("start_date", datetime.now().strftime("%Y-%m-%d")),
                    "duration": preferences.get("duration", len(itinerary_data["days"])),
                    "budget": preferences.get("budget", 0),
                    "travel_style": preferences.get("travel_style", "Not specified"),
                    "interests": preferences.get("interests", [])
                })
                
                return itinerary_data
            return None
        except Exception as e:
            print(f"Error extracting itinerary: {str(e)}")
            return None
    
    def _generate_summary(self, itinerary: Dict, preferences: Dict) -> str:
        """Generate a summary of the itinerary."""
        try:
            # Calculate total cost
            total_cost = sum(
                activity["cost"]
                for day in itinerary["days"]
                for activity in day["activities"]
            )
            
            # Calculate remaining budget
            remaining_budget = preferences.get("budget", 0) - total_cost
            
            # Generate highlights
            highlights = []
            for day in itinerary["days"]:
                day_highlights = []
                for activity in day["activities"]:
                    if activity.get("cost", 0) > 0:  # Only include paid activities as highlights
                        day_highlights.append(activity["title"])
                if day_highlights:
                    highlights.append(f"Day {day['day_number']}: {' and '.join(day_highlights)}")
            
            # Format the summary using the shared template
            return format_itinerary_summary(
                total_days=len(itinerary["days"]),
                total_cost=total_cost,
                remaining_budget=remaining_budget,
                highlights=highlights
            )
            
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return "Error generating summary" 