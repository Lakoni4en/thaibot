import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from config.settings import LEVEL_TRAVEL_API_URL, HEADERS, SEARCH_PARAMS

logger = logging.getLogger(__name__)

@dataclass
class Tour:
    tour_id: str
    title: str
    price: int
    departure_date: str
    nights: int
    hotel_name: str
    hotel_rating: int
    meal_type: str
    flight_info: str
    url: str

def parse_tours() -> List[Tour]:
    """
    Parse tours from Level.Travel API
    """
    try:
        params = SEARCH_PARAMS.copy()
        response = requests.get(
            LEVEL_TRAVEL_API_URL,
            params=params,
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch tours: {response.status_code} {response.text}")
            return []
        
        data = response.json()
        
        if not data.get('results'):
            logger.info("No tours found")
            return []
        
        tours = []
        for item in data['results']:
            try:
                tour = Tour(
                    tour_id=item['id'],
                    title=item['title'],
                    price=int(item['price']['amount']),
                    departure_date=item['departure_date'],
                    nights=item['nights'],
                    hotel_name=item['hotel']['name'],
                    hotel_rating=item['hotel']['rating'],
                    meal_type=item['meal_type'],
                    flight_info=item.get('flight_info', 'Unknown'),
                    url=f"https://level.travel{item['url']}"
                )
                tours.append(tour)
            except KeyError as e:
                logger.warning(f"Missing field in tour data: {e}")
                continue
        
        logger.info(f"Parsed {len(tours)} tours")
        return tours
        
    except Exception as e:
        logger.error(f"Error parsing tours: {e}")
        return []

def get_new_tours(existing_ids: List[str]) -> List[Tour]:
    """
    Get only new tours that are not in existing_ids
    """
    all_tours = parse_tours()
    return [tour for tour in all_tours if tour.tour_id not in existing_ids]