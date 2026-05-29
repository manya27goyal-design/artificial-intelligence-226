"""
Test Cases for Assignment 3: Knowledge Graphs
Run:  python test_knowledge_graphs.py
"""
import sys
sys.path.insert(0, '.')
from knowledge_graphs import KnowledgeGraph, build_rajasthan_kg

PASS = "✓ PASS"; FAIL = "✗ FAIL"
results = []

def check(name, cond, detail=""):
    status = PASS if cond else FAIL
    results.append((name, cond))
    print(f"  {status}  {name}", f"({detail})" if detail else "")

print("\n" + "="*60)
print("SECTION 1: KnowledgeGraph Core")
print("="*60)

kg = KnowledgeGraph("Test")
kg.add_triple("A","rdf:type","Animal")
kg.add_triple("B","rdf:type","Animal")
kg.add_triple("Animal","rdfs:subClassOf","LivingThing")
kg.add_triple("A","name","Alice")

check("Triple count after 4 adds", kg.stats()["triples"] == 4, f"{kg.stats()['triples']}")
check("Query by subject works", len(kg.query(s="A")) == 2)
check("Query by predicate works", len(kg.query(p="rdf:type")) == 2)
check("Query by object works", len(kg.query(o="Animal")) == 2)
check("Full wildcard returns all", len(kg.query()) == 4)
check("Describe A returns dict", "rdf:type" in kg.describe("A"))
check("Entities includes A and B", {"A","B"} <= kg.entities())

# Duplicate triple not stored twice
kg.add_triple("A","rdf:type","Animal")
check("Duplicate triple not stored", kg.stats()["triples"] == 4)

print("\n" + "="*60)
print("SECTION 2: RDFS Inference")
print("="*60)

kg.infer_subclass_types()
inferred = kg.query(s="A", p="rdf:type", o="LivingThing")
check("Inferred A rdf:type LivingThing via subClassOf", len(inferred) == 1)
inferred_b = kg.query(s="B", p="rdf:type", o="LivingThing")
check("Inferred B rdf:type LivingThing via subClassOf", len(inferred_b) == 1)

# Multi-level subclass chain
kg2 = KnowledgeGraph("chain")
kg2.add_triple("x","rdf:type","Dog")
kg2.add_triple("Dog","rdfs:subClassOf","Mammal")
kg2.add_triple("Mammal","rdfs:subClassOf","Animal")
kg2.infer_subclass_types()
check("Multi-level: x inferred as Mammal", len(kg2.query(s="x",p="rdf:type",o="Mammal")) == 1)
check("Multi-level: x inferred as Animal", len(kg2.query(s="x",p="rdf:type",o="Animal")) == 1)

print("\n" + "="*60)
print("SECTION 3: Rajasthan Tourism KG")
print("="*60)

rkg = build_rajasthan_kg()
stats = rkg.stats()
check("KG has > 30 triples", stats["triples"] > 30, f"{stats['triples']}")
check("KG has > 10 entities", stats["entities"] > 10, f"{stats['entities']}")

forts = rkg.query(p="rdf:type", o="Fort")
check("Forts found: at least 2", len(forts) >= 2, f"{len(forts)}")

# Inference: Forts should also be TouristAttractions after inference
attractions = rkg.query(p="rdf:type", o="TouristAttraction")
check("Inference: TouristAttractions inferred", len(attractions) > 0, f"{len(attractions)}")

# Heritage monuments inferred
heritage = rkg.query(p="rdf:type", o="HeritageMonument")
check("Inference: HeritageMonuments inferred", len(heritage) > 0, f"{len(heritage)}")

# Mehrangarh is in Jodhpur
meh_loc = rkg.query(s="MehrangarhFort", p="locatedIn", o="Jodhpur")
check("MehrangarhFort locatedIn Jodhpur", len(meh_loc) == 1)

# Capital query
cap = rkg.query(p="isCapitalOf", o="Rajasthan")
check("Jaipur isCapitalOf Rajasthan", len(cap) == 1 and cap[0][0] == "Jaipur")

# Describe Jodhpur
desc = rkg.describe("Jodhpur")
check("Jodhpur description has knownAs", "knownAs" in desc)
check("Jodhpur knownAs BlueCity", "BlueCity" in desc.get("knownAs",[]))

# Turtle output
ttl = rkg.to_turtle()
check("Turtle output non-empty", len(ttl) > 100)
check("Turtle output contains subject URI", "<MehrangarhFort>" in ttl)

print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
total = len(results)
passed = sum(1 for _, ok in results if ok)
print(f"  Total : {total}")
print(f"  Passed: {passed}  {PASS}")
print(f"  Failed: {total-passed}  {'' if total==passed else FAIL}")
for n, ok in results:
    if not ok: print(f"    FAIL: {n}")
