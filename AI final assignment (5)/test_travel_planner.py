"""
Test Cases for Assignment 2: AI Travel Planner
================================================
Run:  python test_travel_planner.py
"""
import sys
sys.path.insert(0, '.')
from travel_planner import (
    UserPreferences, TourPlanner, PlacesKB, FoodKB, CostKB,
    PLACES_KB, FOOD_KB, Itinerary
)

PASS = "✓ PASS"; FAIL = "✗ FAIL"
results = []

def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((name, condition))
    print(f"  {status}  {name}", f"({detail})" if detail else "")

planner = TourPlanner()

# ─── PlacesKB ────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 1: Places Knowledge Base")
print("="*60)

kb = PlacesKB()
india = kb.filter(country="India")
check("India filter returns places", len(india) > 0, f"count={len(india)}")
check("India filter: all places are Indian", all(p.country == "India" for p in india))

heritage = kb.filter(country="India", category="heritage")
check("Heritage filter works", all(p.category == "heritage" for p in heritage))

high = kb.filter(min_rating=4.7)
check("Min rating 4.7 respected", all(p.rating >= 4.7 for p in high), f"count={len(high)}")

jan = kb.filter(month=1)
check("Month filter (January): places in season", all(1 in p.best_season for p in jan))

tagged = kb.filter(tags=["safari"])
check("Tag search finds wildlife places", any("safari" in p.tags for p in tagged))

sorted_places = kb.filter(country="India")
check("Results sorted by rating descending",
      all(sorted_places[i].rating >= sorted_places[i+1].rating
          for i in range(len(sorted_places)-1)))

# ─── FoodKB ──────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 2: Food Knowledge Base")
print("="*60)

fkb = FoodKB()
veg = fkb.recommend(dietary="veg")
check("Veg filter returns only veg dishes", all("veg" in d.dietary for d in veg))

raj = fkb.recommend(region="Rajasthan")
check("Rajasthan regional filter works", len(raj) > 0, f"count={len(raj)}")

mild = fkb.recommend(max_spice=0)
check("Spice filter respected (max=0)", all(d.spice_level == 0 for d in mild))

bk = fkb.recommend(meal_type="breakfast")
check("Meal type filter: only breakfast dishes", all(d.meal_type == "breakfast" for d in bk))

# ─── CostKB ──────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 3: Cost Knowledge Base")
print("="*60)

prefs = UserPreferences(
    country="India", num_days=5, budget_tier="mid",
    activity_type="heritage", dietary="veg",
    transport_mode="taxi_rideshare", travel_month=11,
    interests=["history"]
)
itin, costs = planner.plan(prefs)

check("Cost dict has all keys",
      all(k in costs for k in ["accommodation","transport","activities","food","total"]))
check("Total = sum of components",
      abs(costs["total"] - sum(v for k,v in costs.items() if k != "total")) < 0.01)
check("Accommodation cost positive", costs["accommodation"] > 0)
check("Total cost is positive", costs["total"] > 0)

# ─── TourPlanner end-to-end ───────────────────────────────────
print("\n" + "="*60)
print("SECTION 4: TourPlanner – Itinerary Generation")
print("="*60)

check("Itinerary has correct num_days", itin.num_days == 5)
check("All days list created", len(itin.days) == 5)
check("At least one place on day 1", len(itin.days[0]) > 0)

# No day exceeds daily hour budget
daily_budget = TourPlanner.PACE_HOURS["moderate"]
for d, day in enumerate(itin.days):
    total_h = sum(p.duration_h for p in day)
    check(f"Day {d+1} hours ≤ {daily_budget}h", total_h <= daily_budget,
          f"used={total_h}h")

# No duplicate places across days
all_visited = [p.name for day in itin.days for p in day]
check("No duplicate places in itinerary", len(all_visited) == len(set(all_visited)))

# Food plan populated
check("Food plan has entries", len(itin.food_plan) > 0)
check("Day 1 breakfast present", "day_1_breakfast" in itin.food_plan)
check("Day 1 lunch present", "day_1_lunch" in itin.food_plan)

# Veg preference respected in food
bks = itin.food_plan.get("day_1_breakfast", [])
if bks:
    check("Food honours veg preference", all("veg" in d.dietary for d in bks))

# ─── Different preference profiles ───────────────────────────
print("\n" + "="*60)
print("SECTION 5: Multiple User Profiles")
print("="*60)

# Budget backpacker
p2 = UserPreferences("France", 3, "budget", "heritage", "veg",
                      "local_transit", 6, interests=["art","romantic"])
i2, c2 = planner.plan(p2)
check("France budget plan generated", i2.num_days == 3)
check("France budget costs < luxury", c2["total"] < 1000)

# Luxury nature traveller
p3 = UserPreferences("India", 7, "luxury", "nature", "non-veg",
                      "guided_tour", 11, interests=["wildlife","safari"])
i3, c3 = planner.plan(p3)
check("Luxury nature plan: num days correct", i3.num_days == 7)
check("Luxury costs higher than budget", c3["total"] > c2["total"])

# Adventure seeker
p4 = UserPreferences("Switzerland", 4, "mid", "adventure", "veg",
                      "rental_car", 8, pace="packed")
i4, c4 = planner.plan(p4)
check("Switzerland adventure plan generated", i4.num_days == 4)

# ─── Render output ───────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 6: Itinerary Rendering")
print("="*60)

rendered = planner.render(itin, costs)
check("Rendered output is non-empty", len(rendered) > 100)
check("Rendered output contains country", "INDIA" in rendered)
check("Rendered output contains cost breakdown", "ESTIMATED COSTS" in rendered)
check("Rendered output contains day sections", "DAY 1" in rendered)

print("\n" + rendered)

# ─── Summary ─────────────────────────────────────────────────
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
total = len(results)
passed = sum(1 for _, ok in results if ok)
failed = total - passed
print(f"  Total : {total}")
print(f"  Passed: {passed}  {PASS}")
print(f"  Failed: {failed}  {'' if failed == 0 else FAIL}")
if failed:
    for n, ok in results:
        if not ok: print(f"    - {n}")
