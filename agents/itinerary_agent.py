from typing import Dict, List
import groq
from datetime import datetime, timedelta
import json
import re

class ItineraryAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = groq.Groq(api_key=api_key)
        print("🤖 ItineraryAgent initialized with Groq client")
    
    def generate_itinerary(self, preferences: Dict) -> Dict:
        """
        Generate a detailed day-by-day itinerary based on user preferences.
        
        Args:
            preferences (Dict): Dictionary containing user preferences including:
                - destination
                - start_date
                - duration
                - budget
                - travel_style
                - interests
        
        Returns:
            Dict: Complete itinerary with day-by-day breakdown
        """
        prompt = self._construct_prompt(preferences)
        
        try:
            print("\n📤 Sending request to Groq API...")
            print("📝 Prompt:")
            print("-" * 50)
            print(prompt)
            print("-" * 50)
            
            # Call Groq API with Llama 3.3 70B Versatile model
            start_time = datetime.now()
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a professional travel planner. Create detailed, day-by-day itineraries based on user preferences. Focus on providing realistic and practical travel plans that consider timing, costs, and local attractions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            end_time = datetime.now()
            
            print(f"\n⏱️ API call completed in {(end_time - start_time).total_seconds():.2f} seconds")
            print("\n📥 Received response from Groq API")
            
            # Parse the response and convert to itinerary format
            response_text = completion.choices[0].message.content
            print("\n📋 Raw response:")
            print("-" * 50)
            print(response_text)
            print("-" * 50)
            
            itinerary = self._parse_response_to_itinerary(response_text, preferences)
            print("\n✅ Successfully parsed response into itinerary format")
            
            return itinerary
            
        except Exception as e:
            print(f"\n❌ Error during API call: {str(e)}")
            print("\n🔍 Error details:")
            import traceback
            print(traceback.format_exc())
            raise Exception("Failed to generate itinerary. Please try again or contact support if the issue persists.")
    
    def _construct_prompt(self, preferences: Dict) -> str:
        """Construct the prompt for the AI model."""
        return f"""
        Create a detailed {preferences['duration']}-day itinerary for {preferences['destination']}.
        Budget: ${preferences['budget']}
        Travel Style: {preferences['travel_style']}
        Interests: {', '.join(preferences['interests'])}
        
        Please provide a realistic and practical itinerary that includes:
        1. Appropriate timing for activities (considering opening hours, travel time)
        2. Estimated costs for each activity
        3. Logical grouping of activities by location
        4. Time for meals and breaks
        5. Transportation considerations
        
        IMPORTANT: Your response must be a valid JSON object with the following structure:
        {{
            "days": [
                {{
                    "day_number": 1,
                    "activities": [
                        {{
                            "time": "HH:MM",
                            "title": "Activity name",
                            "description": "Detailed description including location and practical tips",
                            "duration": "X hours",
                            "cost": price_in_dollars,
                            "location": "Specific location or area",
                            "transportation": "How to get there from previous activity"
                        }}
                    ]
                }}
            ]
        }}
        
        Do not include any text before or after the JSON object. The response must be a valid JSON that can be parsed directly.
        """
    
    def _parse_response_to_itinerary(self, response_text: str, preferences: Dict) -> Dict:
        """Parse the AI response into a structured itinerary."""
        try:
            print("\n🔍 Parsing response text...")
            print("Raw response text:")
            print(response_text)
            
            # Try to parse the entire response as JSON first
            try:
                itinerary_data = json.loads(response_text)
                print("✅ Successfully parsed entire response as JSON")
            except json.JSONDecodeError:
                print("⚠️ Could not parse entire response as JSON, trying to extract JSON content...")
                # Find JSON content in the response
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    print("✅ Found JSON content in response")
                    itinerary_data = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in response")
            
            # Validate the structure
            if not isinstance(itinerary_data, dict):
                raise ValueError("Response is not a dictionary")
            
            if "days" not in itinerary_data:
                raise ValueError("Response missing 'days' key")
            
            if not isinstance(itinerary_data["days"], list):
                raise ValueError("'days' is not a list")
            
            # Add metadata
            itinerary_data.update({
                "destination": preferences["destination"],
                "start_date": preferences["start_date"],
                "duration": preferences["duration"],
                "budget": preferences["budget"],
                "travel_style": preferences["travel_style"],
                "interests": preferences["interests"]
            })
            
            print("\n✅ Successfully parsed and structured itinerary data:")
            print(json.dumps(itinerary_data, indent=2))
            return itinerary_data
            
        except Exception as e:
            print(f"\n❌ Error parsing response: {str(e)}")
            print("\n🔍 Error details:")
            import traceback
            print(traceback.format_exc())
            raise Exception("Failed to parse itinerary data. Please try again or contact support if the issue persists.") 