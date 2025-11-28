import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import json
from typing import Dict, List, Any


trip_details = {
    "budget": 0,
    "destinations": [],
    "flights": {},
    "itinerary": {},
    "restaurants": {},
    "user_preferences": {}
}

def get_destination_recommendations(budget: int, destination_type: str = "any") -> dict:
    """Recommends travel destinations in India based on the provided budget.

    Args:
        budget (int): The budget in Indian Rupees for the trip.
        destination_type (str): Type of destination (beach, historical, hill_station, spiritual, adventure)

    Returns:
        dict: Status and recommended destinations or error message.
    """
    global trip_details
    
    if budget <= 0:
        return {
            "status": "error",
            "error_message": "Budget must be a positive number."
        }
    
    # Store budget in session
    trip_details["budget"] = budget
    
    # Comprehensive destination database
    destinations_db = {
        "budget_low": {  # Under 15000
            "beach": [
                {"name": "Pondicherry", "description": "French colonial charm with beautiful beaches", "estimated_cost": 12000},
                {"name": "Varkala, Kerala", "description": "Cliff-top beaches and Ayurvedic treatments", "estimated_cost": 10000}
            ],
            "historical": [
                {"name": "Jaipur, Rajasthan", "description": "Pink City with magnificent forts and palaces", "estimated_cost": 12000},
                {"name": "Varanasi, Uttar Pradesh", "description": "Ancient spiritual city on the Ganges", "estimated_cost": 8000},
                {"name": "Hampi, Karnataka", "description": "UNESCO World Heritage ruins", "estimated_cost": 10000}
            ],
            "hill_station": [
                {"name": "Mcleodganj, Himachal Pradesh", "description": "Dalai Lama's residence with Tibetan culture", "estimated_cost": 11000},
                {"name": "Rishikesh, Uttarakhand", "description": "Yoga capital with river rafting", "estimated_cost": 9000}
            ],
            "spiritual": [
                {"name": "Amritsar, Punjab", "description": "Golden Temple and Sikh heritage", "estimated_cost": 10000},
                {"name": "Pushkar, Rajasthan", "description": "Sacred lake and camel fair", "estimated_cost": 8000}
            ]
        },
        "budget_medium": {  # 15000-30000
            "beach": [
                {"name": "Goa", "description": "Beaches, nightlife, and Portuguese heritage", "estimated_cost": 25000},
                {"name": "Andaman Islands", "description": "Pristine beaches and water sports", "estimated_cost": 28000}
            ],
            "historical": [
                {"name": "Udaipur, Rajasthan", "description": "City of Lakes with royal palaces", "estimated_cost": 22000},
                {"name": "Mysore, Karnataka", "description": "Royal heritage and silk sarees", "estimated_cost": 18000}
            ],
            "hill_station": [
                {"name": "Manali, Himachal Pradesh", "description": "Adventure sports and apple orchards", "estimated_cost": 20000},
                {"name": "Munnar, Kerala", "description": "Tea plantations and misty mountains", "estimated_cost": 19000}
            ],
            "adventure": [
                {"name": "Leh-Ladakh", "description": "High-altitude desert with stunning landscapes", "estimated_cost": 30000}
            ]
        },
        "budget_high": {  # Above 30000
            "beach": [
                {"name": "Lakshadweep", "description": "Coral islands with luxury resorts", "estimated_cost": 45000}
            ],
            "hill_station": [
                {"name": "Kashmir Valley", "description": "Paradise on Earth with houseboats", "estimated_cost": 40000},
                {"name": "Darjeeling, West Bengal", "description": "Tea gardens and Himalayan views", "estimated_cost": 35000}
            ],
            "adventure": [
                {"name": "Spiti Valley", "description": "Remote high-altitude desert", "estimated_cost": 38000}
            ]
        }
    }
    
    # Determine budget category
    if budget < 15000:
        budget_category = "budget_low"
    elif budget < 30000:
        budget_category = "budget_medium"
    else:
        budget_category = "budget_high"
    
    # Filter by destination type
    recommended_destinations = []
    if destination_type.lower() == "any":
        for dest_type, destinations in destinations_db[budget_category].items():
            recommended_destinations.extend(destinations)
    else:
        dest_type_key = destination_type.lower()
        if dest_type_key in destinations_db[budget_category]:
            recommended_destinations = destinations_db[budget_category][dest_type_key]
    
    # Filter by budget
    affordable_destinations = [dest for dest in recommended_destinations if dest["estimated_cost"] <= budget]
    
    if not affordable_destinations:
        return {
            "status": "error",
            "error_message": f"No destinations found within budget of ₹{budget:,}. Consider increasing your budget or choosing a different destination type."
        }
    
    # Store destinations in session
    trip_details["destinations"] = affordable_destinations
    
    # Format response
    destination_list = []
    for dest in affordable_destinations:
        destination_list.append(f"• **{dest['name']}** - {dest['description']} (Est. Cost: ₹{dest['estimated_cost']:,})")
    
    return {
        "status": "success",
        "report": f"Based on your budget of ₹{budget:,}, here are the recommended destinations:\n\n" + "\n".join(destination_list)
    }

def get_flight_recommendations(destination: str, departure_city: str = "Delhi") -> dict:
    """Finds cheap flight options to a destination within the user's budget.

    Args:
        destination (str): The destination city
        departure_city (str): The departure city (default: Delhi)

    Returns:
        dict: Status and flight recommendations or error message.
    """
    global trip_details
    
    # Flight database with approximate prices
    flight_db = {
        "delhi": {
            "jaipur": {"price": 3500, "duration": "1h 15m", "airlines": ["IndiGo", "SpiceJet"]},
            "varanasi": {"price": 4500, "duration": "1h 30m", "airlines": ["Air India", "IndiGo"]},
            "amritsar": {"price": 4000, "duration": "1h 20m", "airlines": ["IndiGo", "Vistara"]},
            "goa": {"price": 8000, "duration": "2h 30m", "airlines": ["IndiGo", "GoAir"]},
            "leh": {"price": 12000, "duration": "1h 45m", "airlines": ["Air India", "Vistara"]},
            "udaipur": {"price": 5500, "duration": "1h 40m", "airlines": ["IndiGo", "SpiceJet"]},
            "pondicherry": {"price": 7000, "duration": "2h 15m", "airlines": ["IndiGo", "Air India"]},
            "manali": {"price": 6000, "duration": "1h 30m", "airlines": ["IndiGo", "SpiceJet"]}
        },
        "mumbai": {
            "goa": {"price": 4500, "duration": "1h 15m", "airlines": ["IndiGo", "GoAir"]},
            "jaipur": {"price": 5000, "duration": "1h 45m", "airlines": ["IndiGo", "SpiceJet"]},
            "udaipur": {"price": 4800, "duration": "1h 30m", "airlines": ["IndiGo", "Vistara"]}
        }
    }
    
    departure_key = departure_city.lower()
    destination_key = destination.lower().split(',')[0].strip()
    
    if departure_key not in flight_db:
        return {
            "status": "error",
            "error_message": f"Flight data not available from {departure_city}. Try Delhi or Mumbai as departure cities."
        }
    
    if destination_key not in flight_db[departure_key]:
        return {
            "status": "error",
            "error_message": f"No direct flights found from {departure_city} to {destination}. Consider alternative routes or transportation."
        }
    
    flight_info = flight_db[departure_key][destination_key]
    
    # Check if flight cost fits in budget
    remaining_budget = trip_details["budget"] - flight_info["price"] * 2  # Round trip
    
    if remaining_budget < 0:
        return {
            "status": "error",
            "error_message": f"Flight costs (₹{flight_info['price'] * 2:,} round trip) exceed your budget. Consider train or bus travel."
        }
    
    # Store flight info
    trip_details["flights"][destination_key] = flight_info
    
    return {
        "status": "success",
        "report": f"Flight options from {departure_city} to {destination}:\n\n"
                 f"• Price: ₹{flight_info['price']:,} (one way), ₹{flight_info['price'] * 2:,} (round trip)\n"
                 f"• Duration: {flight_info['duration']}\n"
                 f"• Airlines: {', '.join(flight_info['airlines'])}\n"
                 f"• Remaining budget after flights: ₹{remaining_budget:,}"
    }

def get_itinerary_recommendations(destination: str) -> dict:
    """Provides top tourist attractions and itinerary for a destination.

    Args:
        destination (str): The destination city

    Returns:
        dict: Status and itinerary recommendations.
    """
    global trip_details
    
    # Itinerary database
    itinerary_db = {
        "jaipur": {
            "duration": "3-4 days",
            "attractions": [
                "Amber Fort - Magnificent hilltop fort with elephant rides",
                "City Palace - Royal residence with museums and courtyards",
                "Hawa Mahal - Iconic Palace of Winds",
                "Jantar Mantar - UNESCO World Heritage astronomical observatory",
                "Nahargarh Fort - Sunset views over the Pink City",
                "Johari Bazaar - Shopping for jewelry and textiles"
            ],
            "activities": ["Heritage walk", "Rajasthani folk dance show", "Camel safari"]
        },
        "goa": {
            "duration": "4-5 days",
            "attractions": [
                "Baga Beach - Water sports and nightlife",
                "Old Goa Churches - UNESCO World Heritage sites",
                "Dudhsagar Falls - Spectacular four-tiered waterfall",
                "Spice Plantations - Guided tours with traditional lunch",
                "Anjuna Flea Market - Shopping and local crafts",
                "Fort Aguada - Portuguese fort with lighthouse"
            ],
            "activities": ["Beach hopping", "Water sports", "River cruise", "Casino visit"]
        },
        "varanasi": {
            "duration": "2-3 days",
            "attractions": [
                "Dashashwamedh Ghat - Evening Ganga Aarti ceremony",
                "Kashi Vishwanath Temple - Sacred Shiva temple",
                "Sarnath - Buddhist pilgrimage site",
                "Manikarnika Ghat - Sacred cremation ghat",
                "Banaras Hindu University - Sprawling campus and museum",
                "Ramnagar Fort - Mughal architecture"
            ],
            "activities": ["Boat ride on Ganges", "Heritage walk", "Silk weaving tour"]
        },
        "leh": {
            "duration": "6-7 days",
            "attractions": [
                "Pangong Lake - Stunning high-altitude lake",
                "Nubra Valley - Sand dunes and double-humped camels",
                "Magnetic Hill - Gravity-defying phenomenon",
                "Thiksey Monastery - Beautiful Buddhist monastery",
                "Khardung La Pass - World's highest motorable road",
                "Leh Palace - Former royal palace with panoramic views"
            ],
            "activities": ["Trekking", "River rafting", "Motorcycle tours", "Meditation"]
        }
    }
    
    destination_key = destination.lower().split(',')[0].strip()
    
    if destination_key not in itinerary_db:
        return {
            "status": "error",
            "error_message": f"Itinerary not available for {destination}. Please contact support for custom itinerary."
        }
    
    itinerary = itinerary_db[destination_key]
    trip_details["itinerary"][destination_key] = itinerary
    
    attractions_list = "\n".join([f"• {attraction}" for attraction in itinerary["attractions"]])
    activities_list = "\n".join([f"• {activity}" for activity in itinerary["activities"]])
    
    return {
        "status": "success",
        "report": f"Recommended itinerary for {destination} ({itinerary['duration']}):\n\n"
                 f"**Top Attractions:**\n{attractions_list}\n\n"
                 f"**Recommended Activities:**\n{activities_list}"
    }

def get_restaurant_recommendations(destination: str) -> dict:
    """Provides affordable restaurant recommendations for a destination.

    Args:
        destination (str): The destination city

    Returns:
        dict: Status and restaurant recommendations.
    """
    global trip_details
    
    # Restaurant database
    restaurant_db = {
        "jaipur": [
            {"name": "Laxmi Misthan Bhandar", "cuisine": "Rajasthani", "price_range": "₹200-400", "specialty": "Dal Baati Churma"},
            {"name": "Chokhi Dhani", "cuisine": "Traditional Rajasthani", "price_range": "₹800-1200", "specialty": "Village-style dining experience"},
            {"name": "Rawat Mishtan Bhandar", "cuisine": "Snacks & Sweets", "price_range": "₹100-300", "specialty": "Pyaaz Kachori"},
            {"name": "Spice Court", "cuisine": "North Indian", "price_range": "₹400-800", "specialty": "Rooftop dining"}
        ],
        "goa": [
            {"name": "Fisherman's Wharf", "cuisine": "Goan Seafood", "price_range": "₹600-1200", "specialty": "Fish Curry Rice"},
            {"name": "Vinayak Family Restaurant", "cuisine": "Goan", "price_range": "₹300-600", "specialty": "Authentic Goan thali"},
            {"name": "Thalassa", "cuisine": "Greek & Goan", "price_range": "₹800-1500", "specialty": "Beachside dining"},
            {"name": "Ritz Classic", "cuisine": "Multi-cuisine", "price_range": "₹400-800", "specialty": "Local Goan dishes"}
        ],
        "varanasi": [
            {"name": "Kashi Chat Bhandar", "cuisine": "Street Food", "price_range": "₹50-150", "specialty": "Tamatar Chat"},
            {"name": "Dolphin Restaurant", "cuisine": "North Indian", "price_range": "₹200-500", "specialty": "Vegetarian thali"},
            {"name": "Ayyar's Cafe", "cuisine": "South Indian", "price_range": "₹150-300", "specialty": "Filter coffee and dosa"},
            {"name": "Baati Chokha", "cuisine": "Bihari", "price_range": "₹100-250", "specialty": "Traditional Baati Chokha"}
        ],
        "leh": [
            {"name": "The Tibetan Kitchen", "cuisine": "Tibetan", "price_range": "₹300-600", "specialty": "Momos and Thukpa"},
            {"name": "Bon Appetit", "cuisine": "Continental", "price_range": "₹400-800", "specialty": "Wood-fired pizza"},
            {"name": "Lamayuru Restaurant", "cuisine": "Ladakhi", "price_range": "₹250-500", "specialty": "Traditional Ladakhi cuisine"},
            {"name": "German Bakery", "cuisine": "Bakery & Cafe", "price_range": "₹200-400", "specialty": "Fresh bread and pastries"}
        ]
    }
    
    destination_key = destination.lower().split(',')[0].strip()
    
    if destination_key not in restaurant_db:
        return {
            "status": "error",
            "error_message": f"Restaurant recommendations not available for {destination}."
        }
    
    restaurants = restaurant_db[destination_key]
    trip_details["restaurants"][destination_key] = restaurants
    
    restaurant_list = []
    for restaurant in restaurants:
        restaurant_list.append(
            f"• {restaurant['name']} - {restaurant['cuisine']} ({restaurant['price_range']})\n"
            f"  Specialty: {restaurant['specialty']}"
        )
    
    return {
        "status": "success",
        "report": f"Recommended affordable restaurants in {destination}:\n\n" + "\n\n".join(restaurant_list)
    }

def generate_trip_pdf(filename: str = "trip_plan.pdf") -> dict:
    """Generates a comprehensive PDF with all trip details.

    Args:
        filename (str): Name of the PDF file to generate

    Returns:
        dict: Status and PDF generation result.
    """
    global trip_details
    
    if not trip_details["destinations"]:
        return {
            "status": "error",
            "error_message": "No trip details available. Please search for destinations first."
        }
    
    try:
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Budget Trip Plan for India", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Budget information
        budget_text = f"Total Budget: ₹{trip_details['budget']:,}"
        budget_para = Paragraph(budget_text, styles['Heading2'])
        story.append(budget_para)
        story.append(Spacer(1, 0.1*inch))
        
        # Destinations
        dest_heading = Paragraph("Recommended Destinations", styles['Heading2'])
        story.append(dest_heading)
        
        for dest in trip_details["destinations"]:
            dest_text = f"• {dest['name']} - {dest['description']} (Est. Cost: ₹{dest['estimated_cost']:,})"
            dest_para = Paragraph(dest_text, styles['Normal'])
            story.append(dest_para)
        
        story.append(Spacer(1, 0.2*inch))
        
        # Flight information
        if trip_details["flights"]:
            flight_heading = Paragraph("Flight Information", styles['Heading2'])
            story.append(flight_heading)
            
            for dest, flight_info in trip_details["flights"].items():
                flight_text = f"To {dest.title()}: ₹{flight_info['price']:,} (one way), Duration: {flight_info['duration']}"
                flight_para = Paragraph(flight_text, styles['Normal'])
                story.append(flight_para)
            
            story.append(Spacer(1, 0.2*inch))
        
        # Itinerary
        if trip_details["itinerary"]:
            itinerary_heading = Paragraph("Detailed Itinerary", styles['Heading2'])
            story.append(itinerary_heading)
            
            for dest, itinerary in trip_details["itinerary"].items():
                dest_heading = Paragraph(f"{dest.title()} ({itinerary['duration']})", styles['Heading3'])
                story.append(dest_heading)
                
                attractions_heading = Paragraph("Top Attractions:", styles['Heading4'])
                story.append(attractions_heading)
                
                for attraction in itinerary["attractions"]:
                    attraction_para = Paragraph(f"• {attraction}", styles['Normal'])
                    story.append(attraction_para)
                
                story.append(Spacer(1, 0.1*inch))
        
        # Restaurant recommendations
        if trip_details["restaurants"]:
            restaurant_heading = Paragraph("Restaurant Recommendations", styles['Heading2'])
            story.append(restaurant_heading)
            
            for dest, restaurants in trip_details["restaurants"].items():
                dest_heading = Paragraph(f"{dest.title()}", styles['Heading3'])
                story.append(dest_heading)
                
                for restaurant in restaurants:
                    restaurant_text = f"• {restaurant['name']} - {restaurant['cuisine']} ({restaurant['price_range']})"
                    restaurant_para = Paragraph(restaurant_text, styles['Normal'])
                    story.append(restaurant_para)
                
                story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        
        return {
            "status": "success",
            "report": f"Trip plan PDF generated successfully: {filename}",
            "filename": filename
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to generate PDF: {str(e)}"
        }

def update_trip_details(section: str, data: dict) -> dict:
    """Updates specific sections of trip details.

    Args:
        section (str): Section to update (destinations, flights, itinerary, restaurants)
        data (dict): Data to store in the section

    Returns:
        dict: Status of the update operation.
    """
    global trip_details
    
    valid_sections = ["destinations", "flights", "itinerary", "restaurants", "user_preferences"]
    
    if section not in valid_sections:
        return {
            "status": "error",
            "error_message": f"Invalid section. Valid sections: {', '.join(valid_sections)}"
        }
    
    trip_details[section] = data
    
    return {
        "status": "success",
        "report": f"Successfully updated {section} with new data."
    }

def get_trip_summary() -> dict:
    """Provides a comprehensive summary of the current trip plan.

    Returns:
        dict: Complete trip summary.
    """
    global trip_details
    
    if not trip_details["destinations"]:
        return {
            "status": "error",
            "error_message": "No trip details available. Please search for destinations first."
        }
    
    summary_parts = []
    
    # Budget
    summary_parts.append(f"**Budget:** ₹{trip_details['budget']:,}")
    
    # Destinations
    summary_parts.append(f"\n**Destinations ({len(trip_details['destinations'])}):**")
    for dest in trip_details["destinations"]:
        summary_parts.append(f"• {dest['name']} - ₹{dest['estimated_cost']:,}")
    
    # Flights
    if trip_details["flights"]:
        summary_parts.append(f"\n**Flights:**")
        for dest, flight in trip_details["flights"].items():
            summary_parts.append(f"• To {dest.title()}: ₹{flight['price'] * 2:,} (round trip)")
    
    # Itinerary count
    if trip_details["itinerary"]:
        summary_parts.append(f"\n**Itineraries:** {len(trip_details['itinerary'])} destinations planned")
    
    # Restaurant count
    if trip_details["restaurants"]:
        summary_parts.append(f"\n**Restaurants:** {len(trip_details['restaurants'])} destinations covered")
    
    return {
        "status": "success",
        "report": "\n".join(summary_parts)
    }

def get_hotel_recommendations(destination: str) -> dict:
    """Recommends hotels for a specified destination in India.

    Args:
        destination (str): The name of the city or state for hotel recommendations.

    Returns:
        dict: Status and recommended hotels or error message.
    """
    destination = destination.lower()
    available_destinations = {
        "jaipur": [
            "Hotel Heritage Inn - Affordable stay with traditional Rajasthani decor.",
            "Rambagh Palace - A luxurious palace hotel experience."
        ],
        "varanasi": [
            "Hotel Surya - Comfortable stay near the ghats.",
            "BrijRama Palace - Heritage hotel with Ganges views."
        ],
        "amritsar": [
            "Hotel City Park - Budget-friendly with proximity to Golden Temple.",
            "Taj Swarna - Modern luxury near key attractions."
        ],
        "leh-ladakh": [
            "The Grand Dragon Ladakh - Premium hotel with mountain views.",
            "Hotel Ladakh Palace - Cozy stay with local charm."
        ],
        "goa": [
            "Casa de Goa - Boutique hotel near the beach.",
            "Taj Exotica Resort & Spa - Luxury resort with private beach access."
        ],
        "udaipur": [
            "Hotel Lakend - Lakeside hotel with stunning views.",
            "The Leela Palace - Opulent stay with royal ambiance."
        ]
    }

    if destination in available_destinations:
        return {
            "status": "success",
            "report": f"Recommended hotels in {destination.title()}:\n" + "\n".join(available_destinations[destination])
        }
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, hotel recommendations for '{destination}' are not available."
        }