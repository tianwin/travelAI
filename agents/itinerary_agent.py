from typing import Dict, List
import groq
from datetime import datetime, timedelta
import json

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
            # Fallback to mock data if API call fails
            print("\n⚠️ Falling back to mock data...")
            return self._generate_mock_itinerary(preferences)
    
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
        
        Please provide the itinerary in the following JSON format:
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
        """
    
    def _parse_response_to_itinerary(self, response_text: str, preferences: Dict) -> Dict:
        """Parse the AI response into a structured itinerary."""
        try:
            print("\n🔍 Parsing response text...")
            # Extract JSON from the response
            import json
            import re
            
            # Find JSON content in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                print("✅ Found JSON content in response")
                itinerary_data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            # Add metadata
            itinerary_data.update({
                "destination": preferences["destination"],
                "start_date": preferences["start_date"],
                "duration": preferences["duration"],
                "budget": preferences["budget"],
                "travel_style": preferences["travel_style"],
                "interests": preferences["interests"]
            })
            
            print("✅ Successfully parsed and structured itinerary data")
            return itinerary_data
            
        except Exception as e:
            print(f"\n❌ Error parsing response: {str(e)}")
            print("\n🔍 Error details:")
            import traceback
            print(traceback.format_exc())
            return self._generate_mock_itinerary(preferences)
    
    def _generate_mock_itinerary(self, preferences: Dict) -> Dict:
        """Generate mock itinerary data for testing."""
        print("\n⚠️ Generating mock itinerary data...")
        itinerary = {
            "destination": preferences["destination"],
            "start_date": preferences["start_date"],
            "duration": preferences["duration"],
            "budget": preferences["budget"],
            "travel_style": preferences["travel_style"],
            "interests": preferences["interests"],
            "days": []
        }
        
        for day in range(1, preferences["duration"] + 1):
            itinerary["days"].append({
                "day_number": day,
                "activities": [
                    {
                        "time": "09:00",
                        "title": f"Activity {day}.1",
                        "description": "Description coming soon...",
                        "duration": "2 hours",
                        "cost": 50,
                        "location": "Location details coming soon...",
                        "transportation": "Transportation details coming soon..."
                    },
                    {
                        "time": "14:00",
                        "title": f"Activity {day}.2",
                        "description": "Description coming soon...",
                        "duration": "3 hours",
                        "cost": 75,
                        "location": "Location details coming soon...",
                        "transportation": "Transportation details coming soon..."
                    }
                ]
            })
        
        print("✅ Mock itinerary generated")
        return itinerary 