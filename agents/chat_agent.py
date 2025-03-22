from typing import Dict, List, Optional
import groq
from datetime import datetime
import json
import re
import yaml
import os
from .markdown_templates import format_activity_description, EXAMPLE_FORMATTED

class ChatAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = groq.Groq(api_key=api_key)
        self.conversation_history = []
        print("🤖 ChatAgent initialized with Groq client")
    
    def process_message(self, message: str, current_itinerary: Optional[Dict] = None) -> Dict:
        """
        Process a user message and generate a response, potentially modifying the itinerary.
        
        Args:
            message (str): User's message
            current_itinerary (Dict, optional): Current itinerary to modify
            
        Returns:
            Dict: Response containing message and modified itinerary (if applicable)
        """
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": message})
            
            # Prepare the system message
            system_message = f"""You are a helpful travel assistant. You can help users modify their travel itineraries and answer questions about their trips.
            
            When modifying an itinerary, you should:
            1. Keep the same JSON structure
            2. Use markdown formatting in descriptions for better readability
            3. Highlight important information using bold and italics
            4. Use bullet points for lists of items
            5. Format costs and times consistently
            
            Example of how to format activity descriptions:
            {{
                "days": [
                    {{
                        "day_number": 1,
                        "activities": [
                            {{
                                "time": "09:00",
                                "title": "Activity Name",
                                "description": "{EXAMPLE_FORMATTED}",
                                "duration": "2 hours",
                                "cost": 30,
                                "location": "Buckingham Palace, London SW1A 1AA",
                                "transportation": "Take the Tube to Green Park Station, then walk 5 minutes"
                            }}
                        ]
                    }}
                ]
            }}
            
            Always maintain the JSON structure while adding markdown formatting to the text fields."""
            
            # Prepare the context with current itinerary if available
            context = ""
            if current_itinerary:
                # Include all activity details but limit the description length
                simplified_itinerary = {
                    "days": [
                        {
                            "day_number": day["day_number"],
                            "activities": [
                                {
                                    "time": activity["time"],
                                    "title": activity["title"],
                                    "duration": activity["duration"],
                                    "cost": activity["cost"],
                                    "location": activity["location"],
                                    "transportation": activity["transportation"],
                                    "description": activity["description"][:100] + "..." if len(activity["description"]) > 100 else activity["description"]
                                }
                                for activity in day["activities"]
                            ]
                        }
                        for day in current_itinerary["days"]
                    ],
                    "destination": current_itinerary.get("destination", "Unknown Destination"),
                    "duration": current_itinerary.get("duration", len(current_itinerary["days"]))
                }
                context = f"""Current itinerary:
{json.dumps(simplified_itinerary, indent=2)}

Please use this current itinerary as a reference and make modifications based on the user's request. If the user asks about the current itinerary, provide information from this data. If they request changes, modify this specific itinerary while maintaining its structure. Make sure to preserve all activity details and only update what the user specifically requests to change."""
            
            # Limit conversation history to last 3 messages
            recent_history = self.conversation_history[-3:] if len(self.conversation_history) > 3 else self.conversation_history
            
            # Prepare the messages for the API
            messages = [
                {"role": "system", "content": system_message + "\n\n" + context if context else system_message},
                *recent_history
            ]
            
            # Call Groq API
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=4000
            )
            
            # Get the response
            response_text = completion.choices[0].message.content
            
            # Try to extract itinerary modifications if present
            modified_itinerary = self._extract_itinerary_modifications(response_text)
            
            # If modifications were found, merge them with the current itinerary
            if modified_itinerary and current_itinerary:
                for day in modified_itinerary["days"]:
                    # Find matching day in current itinerary
                    current_day = next((d for d in current_itinerary["days"] if d["day_number"] == day["day_number"]), None)
                    if current_day:
                        for activity in day["activities"]:
                            # Find matching activity in current day
                            current_activity = next((a for a in current_day["activities"] if a["title"] == activity["title"]), None)
                            if current_activity:
                                # Update only the changed fields
                                for key, value in activity.items():
                                    if key != "description" or value != current_activity[key]:
                                        current_activity[key] = value
                
                # Use the updated current itinerary
                modified_itinerary = current_itinerary
            
            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return {
                "message": response_text,
                "modified_itinerary": modified_itinerary
            }
            
        except Exception as e:
            print(f"Error in process_message: {str(e)}")
            return {
                "message": f"I apologize, but I encountered an error: {str(e)}",
                "modified_itinerary": None
            }
    
    def _extract_itinerary_modifications(self, response_text: str) -> Optional[Dict]:
        """Extract itinerary modifications from the response text."""
        try:
            # Look for JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                
                try:
                    # First try to parse the JSON directly
                    itinerary_data = json.loads(json_str)
                except json.JSONDecodeError:
                    try:
                        # If that fails, try to clean and parse the JSON
                        # First, normalize newlines and remove any control characters
                        json_str = json_str.replace('\r\n', '\n').replace('\r', '\n')
                        json_str = ''.join(char for char in json_str if ord(char) >= 32 or char == '\n')
                        
                        # Handle markdown formatting in strings
                        json_str = re.sub(r'(\w+):\s*"([^"]*)"', lambda m: f'{m.group(1)}: "{m.group(2).replace("**", "").replace("*", "").replace("`", "")}"', json_str)
                        
                        # Replace newlines in strings with \n
                        in_string = False
                        cleaned_str = []
                        i = 0
                        while i < len(json_str):
                            char = json_str[i]
                            if char == '"' and (i == 0 or json_str[i-1] != '\\'):
                                in_string = not in_string
                            if char == '\n' and in_string:
                                cleaned_str.append('\\n')
                            else:
                                cleaned_str.append(char)
                            i += 1
                        
                        json_str = ''.join(cleaned_str)
                        
                        # Try to parse the cleaned JSON
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
                        
                        # Format the description using the template
                        activity["description"] = format_activity_description(
                            title=activity["title"],
                            description=activity["description"],
                            location_details={"Address": activity["location"]},
                            transportation=activity["transportation"]
                        )
                
                return itinerary_data
            
            return None
            
        except Exception as e:
            print(f"Error in _extract_itinerary_modifications: {str(e)}")
            return None
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = [] 