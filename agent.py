import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import json
from typing import Dict, List, Any
from tools.planning_tools import (
    get_destination_recommendations,
    get_hotel_recommendations,
    get_flight_recommendations,
    get_itinerary_recommendations,
    get_restaurant_recommendations,
    get_trip_summary
)

root_agent = Agent(
    name="planning_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_destination_recommendations,
    get_hotel_recommendations,
    get_flight_recommendations,
    get_itinerary_recommendations,
    get_restaurant_recommendations,
    get_trip_summary],
)