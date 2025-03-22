import yaml
import groq
from agents.itinerary_agent import ItineraryAgent
import json
from datetime import datetime

def load_config():
    print("\n📂 Loading configuration from config.yaml...")
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print("✅ Configuration loaded successfully")
    return config

def test_groq_connection():
    config = load_config()
    api_key = config['api_keys']['groq']
    
    try:
        print("\n🤖 Initializing ItineraryAgent...")
        agent = ItineraryAgent(api_key)
        print("✅ ItineraryAgent initialized successfully")
        
        # Test preferences
        test_preferences = {
            "destination": "San Francisco",
            "start_date": "2024-04-01",
            "duration": 2,
            "budget": 1000,
            "travel_style": "Comfort",
            "interests": ["Food", "Culture", "Nature"]
        }
        
        print("\n📝 Test preferences:")
        print(json.dumps(test_preferences, indent=2))
        
        print("\n🚀 Generating itinerary using Groq API...")
        print(f"Model: {config['models']['llm']['name']}")
        print(f"Temperature: {config['models']['llm']['temperature']}")
        print(f"Max tokens: {config['models']['llm']['max_tokens']}")
        
        start_time = datetime.now()
        itinerary = agent.generate_itinerary(test_preferences)
        end_time = datetime.now()
        
        print(f"\n⏱️ API call duration: {(end_time - start_time).total_seconds():.2f} seconds")
        print("\n✅ Itinerary generated successfully!")
        
        print("\n📋 Generated itinerary summary:")
        print(f"Destination: {itinerary['destination']}")
        print(f"Duration: {itinerary['duration']} days")
        print(f"Budget: ${itinerary['budget']}")
        print(f"Travel Style: {itinerary['travel_style']}")
        print(f"Interests: {', '.join(itinerary['interests'])}")
        
        print("\n📅 First day activities:")
        for activity in itinerary['days'][0]['activities']:
            print(f"\n⏰ {activity['time']}: {activity['title']}")
            print(f"   📍 Location: {activity.get('location', 'Not specified')}")
            print(f"   💰 Cost: ${activity['cost']}")
            print(f"   ⏱️ Duration: {activity['duration']}")
            print(f"   🚌 Transportation: {activity.get('transportation', 'Not specified')}")
            print(f"   📝 Description: {activity['description']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        print("\n🔍 Error details:")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("🚀 Testing AI Travel Planner setup...")
    print("=" * 50)
    success = test_groq_connection()
    print("=" * 50)
    if success:
        print("\n✨ Setup completed successfully! You can now run the main application.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.") 