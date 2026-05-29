"""
Assignment 2: AI-Based Travel Planner with Knowledge Bases
============================================================
Reuses existing knowledge in multiple domains:
  • Tourist Places ontology (destinations, categories, ratings)
  • Food Recommendation KB  (regional cuisine, dietary preferences)
  • Tour Plan Generator     (itinerary builder, day-by-day scheduling)
  • Cost Assessment KB      (accommodation, transport, activities)

The planner accepts user preferences and produces a personalised,
costed itinerary using rule-based inference over these KBs.

Author: AI Assignments
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import random


# ─────────────────────────────────────────────────────────────
# KNOWLEDGE BASE 1 – TOURIST PLACES ONTOLOGY
# ─────────────────────────────────────────────────────────────

@dataclass
class Place:
    """
    Represents a tourist attraction.

    Attributes:
        name       : Display name
        city       : City where the place is located
        country    : Country
        category   : 'heritage' | 'nature' | 'adventure' | 'religious' | 'beach'
        rating     : 1-5 star rating (float)
        duration_h : Typical visit duration in hours
        best_season: List of suitable months (1-12)
        indoor     : Whether the place is indoors (weather-insensitive)
        tags       : Free-form tags for preference matching
    """
    name: str
    city: str
    country: str
    category: str
    rating: float
    duration_h: float
    best_season: List[int]
    indoor: bool
    tags: List[str]


# ── Places KB ─────────────────────────────────────────────────

PLACES_KB: List[Place] = [
    # ─── India ───────────────────────────────────────────────
    Place("Taj Mahal",          "Agra",       "India", "heritage",   5.0, 3.0, list(range(10,13))+[1,2], False, ["unesco","mughal","architecture","iconic"]),
    Place("Jaipur City Palace", "Jaipur",     "India", "heritage",   4.5, 2.5, [10,11,12,1,2,3],          True,  ["rajput","palace","art","history"]),
    Place("Mehrangarh Fort",    "Jodhpur",    "India", "heritage",   4.7, 3.0, [10,11,12,1,2,3],          False, ["fort","rajput","panoramic","history"]),
    Place("Umaid Bhawan Palace","Jodhpur",    "India", "heritage",   4.3, 1.5, [10,11,12,1,2,3],          True,  ["palace","luxury","museum","jodhpur"]),
    Place("Ranthambore NP",     "Sawai",      "India", "nature",     4.6, 6.0, [10,11,12,1,2,3,4],        False, ["tigers","safari","wildlife","jungle"]),
    Place("Varanasi Ghats",     "Varanasi",   "India", "religious",  4.8, 4.0, [10,11,12,1,2],            False, ["ganges","spiritual","hindu","cultural"]),
    Place("Kerala Backwaters",  "Alleppey",   "India", "nature",     4.7, 8.0, [9,10,11,12,1,2,3],        False, ["houseboat","nature","serene","beach"]),
    Place("Goa Beach Cruise",   "Goa",        "India", "beach",      4.2, 5.0, [10,11,12,1,2,3],          False, ["beach","party","nightlife","sun"]),
    Place("Amber Fort",         "Jaipur",     "India", "heritage",   4.6, 2.5, [10,11,12,1,2,3],          False, ["fort","elephant","history","rajasthan"]),
    Place("Hampi Ruins",        "Hampi",      "India", "heritage",   4.5, 5.0, [10,11,12,1,2,3],          False, ["ruins","vijayanagara","boulders","history"]),
    Place("Munnar Tea Gardens", "Munnar",     "India", "nature",     4.4, 3.0, [9,10,11,12,1,2,3],        False, ["tea","hills","nature","scenic"]),

    # ─── Europe ──────────────────────────────────────────────
    Place("Eiffel Tower",       "Paris",      "France",  "heritage", 4.6, 2.0, list(range(4,11)),          False, ["iconic","architecture","romantic","city"]),
    Place("Louvre Museum",      "Paris",      "France",  "heritage", 4.7, 4.0, list(range(1,13)),           True,  ["art","museum","mona lisa","history"]),
    Place("Colosseum",          "Rome",       "Italy",   "heritage", 4.7, 2.5, [3,4,5,9,10,11],            False, ["roman","history","architecture","iconic"]),
    Place("Amalfi Coast",       "Amalfi",     "Italy",   "beach",    4.8, 6.0, [5,6,7,8,9,10],             False, ["beach","scenic","coastal","luxury"]),
    Place("Sagrada Familia",    "Barcelona",  "Spain",   "heritage", 4.7, 2.0, list(range(1,13)),           True,  ["gaudi","architecture","religious","art"]),
    Place("Alhambra",           "Granada",    "Spain",   "heritage", 4.8, 3.5, [3,4,5,9,10,11],            False, ["moorish","palace","history","garden"]),
    Place("Swiss Alps Hike",    "Interlaken", "Switzerland","adventure",4.9,8.0,[6,7,8,9],                  False, ["hiking","mountains","snow","adventure"]),
    Place("Amsterdam Canals",   "Amsterdam",  "Netherlands","nature", 4.5, 3.0, [4,5,6,7,8,9,10],           False, ["canals","bikes","culture","tulips"]),

    # ─── Asia-Pacific ─────────────────────────────────────────
    Place("Bali Rice Terraces", "Ubud",       "Indonesia","nature",  4.6, 4.0, [4,5,6,7,8,9],              False, ["rice","nature","spiritual","tropical"]),
    Place("Angkor Wat",         "Siem Reap",  "Cambodia","heritage", 4.9, 6.0, [11,12,1,2,3,4],            False, ["khmer","temple","history","iconic"]),
    Place("Mount Fuji",         "Hakone",     "Japan",   "nature",   4.9, 8.0, [7,8,9],                    False, ["volcano","hiking","iconic","scenic"]),
    Place("Tokyo Senso-ji",     "Tokyo",      "Japan",   "religious",4.5, 1.5, list(range(1,13)),           False, ["temple","history","culture","shopping"]),
]


class PlacesKB:
    """Query interface for the Tourist Places knowledge base."""

    def __init__(self, places: List[Place] = PLACES_KB):
        self.places = places

    def filter(self,
               country: Optional[str] = None,
               city: Optional[str] = None,
               category: Optional[str] = None,
               min_rating: float = 0.0,
               month: Optional[int] = None,
               tags: Optional[List[str]] = None) -> List[Place]:
        results = self.places
        if country:
            results = [p for p in results if p.country.lower() == country.lower()]
        if city:
            results = [p for p in results if p.city.lower() == city.lower()]
        if category:
            results = [p for p in results if p.category == category]
        if min_rating:
            results = [p for p in results if p.rating >= min_rating]
        if month:
            results = [p for p in results if month in p.best_season]
        if tags:
            results = [p for p in results
                       if any(t.lower() in p.tags for t in tags)]
        return sorted(results, key=lambda p: -p.rating)

    def recommend(self, preferences: 'UserPreferences') -> List[Place]:
        """Rule-based recommendation from user preferences."""
        return self.filter(
            country=preferences.country,
            category=preferences.activity_type,
            min_rating=preferences.min_rating,
            month=preferences.travel_month,
            tags=preferences.interests
        )


# ─────────────────────────────────────────────────────────────
# KNOWLEDGE BASE 2 – FOOD RECOMMENDATION
# ─────────────────────────────────────────────────────────────

@dataclass
class Dish:
    name: str
    cuisine: str
    region: str
    dietary: List[str]     # 'veg', 'vegan', 'non-veg', 'gluten-free', 'halal'
    meal_type: str         # 'breakfast' | 'lunch' | 'dinner' | 'snack'
    spice_level: int       # 0=mild, 1=medium, 2=hot, 3=very_hot
    avg_cost_usd: float
    description: str


FOOD_KB: List[Dish] = [
    # ─── Indian ──────────────────────────────────────────────
    Dish("Dal Baati Churma",     "Rajasthani","Rajasthan","veg",       "lunch",   1, 4.0,  "Lentil balls baked in ghee, Rajasthan staple"),
    Dish("Laal Maas",            "Rajasthani","Rajasthan","non-veg",   "dinner",  3, 6.0,  "Fiery red mutton curry with Mathania chillies"),
    Dish("Pyaaz Kachori",        "Rajasthani","Rajasthan","veg",       "breakfast",0,1.5,  "Deep-fried pastry stuffed with spiced onion"),
    Dish("Butter Chicken",       "North Indian","Punjab",  "non-veg",  "dinner",  1, 5.0,  "Creamy tomato-based chicken curry"),
    Dish("Masala Dosa",          "South Indian","Karnataka","veg",     "breakfast",1, 2.0,  "Crispy rice crepe with spiced potato filling"),
    Dish("Kerala Fish Curry",    "South Indian","Kerala",  "non-veg",  "lunch",   2, 6.0,  "Coconut milk fish curry with raw mango"),
    Dish("Pav Bhaji",            "Maharashtrian","Mumbai","veg",       "snack",   1, 2.0,  "Spiced vegetable mash with buttered bread"),
    Dish("Biryani",              "Mughlai",   "Hyderabad","non-veg",   "lunch",   2, 5.0,  "Aromatic slow-cooked rice with meat"),
    # ─── Continental ─────────────────────────────────────────
    Dish("Croissant",            "French",    "Paris",    "veg",       "breakfast",0, 3.0, "Buttery flaky pastry"),
    Dish("Ratatouille",          "French",    "Provence", "vegan",     "dinner",  0, 12.0, "Provençal vegetable stew"),
    Dish("Pizza Margherita",     "Italian",   "Naples",   "veg",       "lunch",   0, 8.0,  "Tomato, mozzarella, basil on thin crust"),
    Dish("Pasta Carbonara",      "Italian",   "Rome",     "non-veg",   "dinner",  0, 10.0, "Egg and pecorino sauce with guanciale"),
    Dish("Paella",               "Spanish",   "Valencia", "non-veg",   "lunch",   0, 12.0, "Saffron rice with seafood and chicken"),
    Dish("Tapas Assortment",     "Spanish",   "Barcelona","veg",       "snack",   0, 8.0,  "Assorted small bites"),
    # ─── Asian ───────────────────────────────────────────────
    Dish("Nasi Goreng",          "Indonesian","Bali",     "non-veg",   "lunch",   1, 3.0,  "Fried rice with egg, chicken, vegetables"),
    Dish("Sushi Platter",        "Japanese",  "Tokyo",    "non-veg",   "lunch",   0, 20.0, "Fresh nigiri and maki assortment"),
    Dish("Ramen",                "Japanese",  "Tokyo",    "non-veg",   "dinner",  1, 10.0, "Wheat noodles in rich broth"),
    Dish("Amok Fish",            "Cambodian", "Siem Reap","non-veg",  "dinner",  1, 5.0,  "Steamed fish in coconut and lemongrass"),
]


class FoodKB:
    """Query interface for the Food Recommendation knowledge base."""

    def __init__(self, dishes: List[Dish] = FOOD_KB):
        self.dishes = dishes

    def recommend(self,
                  region: Optional[str] = None,
                  dietary: Optional[str] = None,
                  meal_type: Optional[str] = None,
                  max_spice: int = 3,
                  max_cost: float = 999) -> List[Dish]:
        results = self.dishes
        if region:
            results = [d for d in results
                       if region.lower() in d.region.lower()
                       or region.lower() in d.cuisine.lower()]
        if dietary:
            results = [d for d in results if dietary.lower() in d.dietary]
        if meal_type:
            results = [d for d in results if d.meal_type == meal_type]
        results = [d for d in results if d.spice_level <= max_spice]
        results = [d for d in results if d.avg_cost_usd <= max_cost]
        return results


# ─────────────────────────────────────────────────────────────
# KNOWLEDGE BASE 3 – COST ASSESSMENT
# ─────────────────────────────────────────────────────────────

# Accommodation costs per night (USD) by budget tier
ACCOMMODATION_KB: Dict[str, Dict[str, float]] = {
    "budget":  {"India":50,  "France":60,  "Italy":65, "Spain":55, "Indonesia":35, "Japan":50},
    "mid":     {"India":120, "France":180, "Italy":170,"Spain":150,"Indonesia":100,"Japan":150},
    "luxury":  {"India":300, "France":450, "Italy":400,"Spain":380,"Indonesia":250,"Japan":380},
}

# Transport costs per travel day (USD) by mode
TRANSPORT_KB: Dict[str, float] = {
    "local_transit": 5,
    "taxi_rideshare": 20,
    "rental_car": 50,
    "guided_tour": 80,
}

# Activity/entrance fees KB (USD) mapped to place names
ACTIVITY_FEES_KB: Dict[str, float] = {
    "Taj Mahal": 15, "Jaipur City Palace": 8, "Mehrangarh Fort": 7,
    "Ranthambore NP": 30, "Kerala Backwaters": 60, "Varanasi Ghats": 5,
    "Hampi Ruins": 10, "Amber Fort": 8, "Goa Beach Cruise": 25,
    "Eiffel Tower": 25, "Louvre Museum": 22, "Colosseum": 18,
    "Sagrada Familia": 26, "Alhambra": 15, "Swiss Alps Hike": 0,
    "Amsterdam Canals": 18, "Bali Rice Terraces": 5, "Angkor Wat": 37,
    "Mount Fuji": 10, "Tokyo Senso-ji": 0, "Amalfi Coast": 20,
    "Paella": 0,  # food has its own cost
}

# Meal cost per day (USD) by budget
MEAL_COST_PER_DAY: Dict[str, float] = {
    "budget": 15, "mid": 35, "luxury": 80
}


class CostKB:
    """Estimates trip cost from itinerary."""

    def estimate(self,
                 itinerary: 'Itinerary',
                 budget_tier: str,
                 transport_mode: str,
                 country: str) -> Dict[str, float]:
        days = itinerary.num_days
        acc  = ACCOMMODATION_KB.get(budget_tier, {}).get(country, 100) * days
        trn  = TRANSPORT_KB.get(transport_mode, 20) * days
        act  = sum(ACTIVITY_FEES_KB.get(p.name, 10) for day in itinerary.days for p in day)
        food = MEAL_COST_PER_DAY.get(budget_tier, 35) * days
        total = acc + trn + act + food
        return {"accommodation": acc, "transport": trn,
                "activities": act, "food": food, "total": total}


# ─────────────────────────────────────────────────────────────
# USER PREFERENCES MODEL
# ─────────────────────────────────────────────────────────────

@dataclass
class UserPreferences:
    country: str
    num_days: int
    budget_tier: str       # 'budget' | 'mid' | 'luxury'
    activity_type: Optional[str]   # category filter
    dietary: str           # 'veg' | 'non-veg' | 'vegan'
    transport_mode: str    # 'local_transit' | 'taxi_rideshare' | 'rental_car' | 'guided_tour'
    travel_month: int      # 1-12
    min_rating: float = 4.0
    interests: List[str] = field(default_factory=list)
    max_spice: int = 3
    pace: str = "moderate"    # 'relaxed' | 'moderate' | 'packed'


# ─────────────────────────────────────────────────────────────
# ITINERARY DATA MODEL
# ─────────────────────────────────────────────────────────────

@dataclass
class Itinerary:
    preferences: UserPreferences
    days: List[List[Place]]    # days[i] = list of places on day i+1
    food_plan: Dict[str, List[Dish]]  # 'day_1_breakfast', etc.

    @property
    def num_days(self) -> int:
        return len(self.days)


# ─────────────────────────────────────────────────────────────
# TOUR PLAN GENERATOR (PERSONALISED ITINERARY ENGINE)
# ─────────────────────────────────────────────────────────────

class TourPlanner:
    """
    Rule-based personalised tour planner.

    Workflow:
      1. Query PlacesKB with user preferences → candidate places
      2. Assign places across days respecting daily hour budget
      3. Query FoodKB for regional meal suggestions per day
      4. Query CostKB for final cost estimate
    """

    PACE_HOURS = {"relaxed": 6, "moderate": 8, "packed": 12}

    def __init__(self):
        self.places_kb = PlacesKB()
        self.food_kb   = FoodKB()
        self.cost_kb   = CostKB()

    def plan(self, prefs: UserPreferences) -> Tuple[Itinerary, Dict[str, float]]:
        """Generate itinerary and cost breakdown."""
        # Step 1: Get recommended places
        candidates = self.places_kb.recommend(prefs)
        if not candidates:
            candidates = self.places_kb.filter(country=prefs.country,
                                               min_rating=prefs.min_rating)

        # Step 2: Schedule places across days (greedy bin-packing by hours)
        daily_budget = self.PACE_HOURS.get(prefs.pace, 8)
        days: List[List[Place]] = [[] for _ in range(prefs.num_days)]
        day_hours = [0.0] * prefs.num_days
        used = set()

        for place in candidates:
            if place.name in used:
                continue
            for d in range(prefs.num_days):
                if day_hours[d] + place.duration_h <= daily_budget:
                    days[d].append(place)
                    day_hours[d] += place.duration_h
                    used.add(place.name)
                    break

        # Step 3: Build food plan
        food_plan: Dict[str, List[Dish]] = {}
        region_guess = prefs.country  # crude region mapping
        for d in range(prefs.num_days):
            key = f"day_{d+1}"
            food_plan[f"{key}_breakfast"] = self.food_kb.recommend(
                region=region_guess, dietary=prefs.dietary,
                meal_type="breakfast", max_spice=prefs.max_spice)[:2]
            food_plan[f"{key}_lunch"] = self.food_kb.recommend(
                region=region_guess, dietary=prefs.dietary,
                meal_type="lunch", max_spice=prefs.max_spice)[:2]
            food_plan[f"{key}_dinner"] = self.food_kb.recommend(
                region=region_guess, dietary=prefs.dietary,
                meal_type="dinner", max_spice=prefs.max_spice)[:2]

        itinerary = Itinerary(preferences=prefs, days=days, food_plan=food_plan)

        # Step 4: Cost estimate
        costs = self.cost_kb.estimate(itinerary, prefs.budget_tier,
                                      prefs.transport_mode, prefs.country)

        return itinerary, costs

    # ── Pretty printer ────────────────────────────────────────

    def render(self, itinerary: Itinerary, costs: Dict[str, float]) -> str:
        prefs = itinerary.preferences
        lines = []
        lines.append("=" * 65)
        lines.append(f"  PERSONALISED TRAVEL PLAN — {prefs.country.upper()}")
        lines.append(f"  {prefs.num_days}-Day Trip  |  Budget: {prefs.budget_tier.title()}")
        lines.append(f"  Month: {prefs.travel_month}  |  Pace: {prefs.pace.title()}")
        lines.append("=" * 65)

        for d, day_places in enumerate(itinerary.days):
            lines.append(f"\nDAY {d+1}")
            lines.append("-" * 35)

            bk  = itinerary.food_plan.get(f"day_{d+1}_breakfast", [])
            ln  = itinerary.food_plan.get(f"day_{d+1}_lunch", [])
            din = itinerary.food_plan.get(f"day_{d+1}_dinner", [])

            if bk:  lines.append(f"  ☕ Breakfast: {bk[0].name}")
            if day_places:
                lines.append("  🗺 Places:")
                for p in day_places:
                    lines.append(f"      • {p.name} ({p.city}) [{p.rating}★] ~{p.duration_h}h")
            else:
                lines.append("  🗺 Free day / travel day")
            if ln:  lines.append(f"  🍽 Lunch   : {ln[0].name}")
            if din: lines.append(f"  🌙 Dinner  : {din[0].name}")

        lines.append("\n" + "=" * 65)
        lines.append("  ESTIMATED COSTS (USD)")
        lines.append("-" * 35)
        for k, v in costs.items():
            lines.append(f"  {'Total' if k=='total' else k.title():20s} ${v:>8.2f}")
        lines.append("=" * 65)
        return "\n".join(lines)
