from typing import Dict, List

def format_activity_description(
    title: str,
    description: str,
    tips: List[str] = None,
    notes: List[str] = None,
    location_details: Dict = None,
    transportation: str = None
) -> str:
    """
    Format an activity description with consistent markdown styling.
    
    Args:
        title (str): Activity title
        description (str): Main activity description
        tips (List[str], optional): List of tips for the activity
        notes (List[str], optional): List of important notes
        location_details (Dict, optional): Dictionary containing location information
        transportation (str, optional): Transportation details
    
    Returns:
        str: Formatted markdown description
    """
    parts = []
    
    # Main description
    parts.append(f"**{title}**\n\n{description}")
    
    # Tips section
    if tips:
        parts.append("\n*Important Tips:*")
        for tip in tips:
            parts.append(f"- {tip}")
    
    # Notes section
    if notes:
        parts.append("\n*Important Notes:*")
        for note in notes:
            parts.append(f"> {note}")
    
    # Location details
    if location_details:
        parts.append("\n**Location Details:**")
        for key, value in location_details.items():
            parts.append(f"- {key}: `{value}`")
    
    # Transportation
    if transportation:
        parts.append(f"\n**Getting There:**\n{transportation}")
    
    return "\n".join(parts)

def format_itinerary_summary(
    total_days: int,
    total_cost: float,
    remaining_budget: float,
    highlights: List[str] = None
) -> str:
    """
    Format the itinerary summary with consistent markdown styling.
    
    Args:
        total_days (int): Total number of days
        total_cost (float): Total cost of the itinerary
        remaining_budget (float): Remaining budget
        highlights (List[str], optional): List of trip highlights
    
    Returns:
        str: Formatted markdown summary
    """
    parts = []
    
    # Basic information
    parts.append(f"## Trip Summary\n")
    parts.append(f"- **Duration:** {total_days} days")
    parts.append(f"- **Total Cost:** ${total_cost:.2f}")
    parts.append(f"- **Remaining Budget:** ${remaining_budget:.2f}")
    
    # Highlights
    if highlights:
        parts.append("\n### Trip Highlights")
        for highlight in highlights:
            parts.append(f"- {highlight}")
    
    return "\n".join(parts)

def format_day_summary(
    day_number: int,
    total_cost: float,
    highlights: List[str] = None
) -> str:
    """
    Format a day summary with consistent markdown styling.
    
    Args:
        day_number (int): Day number
        total_cost (float): Total cost for the day
        highlights (List[str], optional): List of day highlights
    
    Returns:
        str: Formatted markdown summary
    """
    parts = []
    
    # Basic information
    parts.append(f"### Day {day_number} Summary")
    parts.append(f"- **Total Cost:** ${total_cost:.2f}")
    
    # Highlights
    if highlights:
        parts.append("\n**Highlights:**")
        for highlight in highlights:
            parts.append(f"- {highlight}")
    
    return "\n".join(parts)

# Example usage:
EXAMPLE_ACTIVITY = {
    "time": "09:00",
    "title": "Activity Name",
    "description": "Start your day with a visit to **Buckingham Palace**, the official residence of the British monarch.",
    "tips": [
        "Book tickets in advance",
        "Arrive 15 minutes early",
        "Photography not allowed inside"
    ],
    "notes": [
        "The Changing of the Guard ceremony takes place at 11:00 AM"
    ],
    "location_details": {
        "Address": "Buckingham Palace, London SW1A 1AA",
        "Nearest Tube": "Green Park Station"
    },
    "transportation": "Take the Tube to Green Park Station, then walk 5 minutes"
}

EXAMPLE_FORMATTED = format_activity_description(
    title=EXAMPLE_ACTIVITY["title"],
    description=EXAMPLE_ACTIVITY["description"],
    tips=EXAMPLE_ACTIVITY["tips"],
    notes=EXAMPLE_ACTIVITY["notes"],
    location_details=EXAMPLE_ACTIVITY["location_details"],
    transportation=EXAMPLE_ACTIVITY["transportation"]
) 