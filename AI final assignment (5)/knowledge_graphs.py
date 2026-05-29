"""
Assignment 3: Knowledge Graphs — Description & Tool Exploration
================================================================
Builds a small Knowledge Graph using NetworkX, demonstrates
SPARQL-like querying via Python, and surveys major KG tools.

A Knowledge Graph (KG) is a structured representation of real-world
entities and the relationships between them, stored as a directed
labelled graph of (subject, predicate, object) triples.

Author: AI Assignments
"""

import json
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Set


# ─────────────────────────────────────────────────────────────
# PART A – CONCEPTUAL OVERVIEW (printed as structured text)
# ─────────────────────────────────────────────────────────────

KG_OVERVIEW = """
╔══════════════════════════════════════════════════════════════╗
║          KNOWLEDGE GRAPHS — DESCRIPTION & TOOLS             ║
╚══════════════════════════════════════════════════════════════╝

1. WHAT IS A KNOWLEDGE GRAPH?
─────────────────────────────
A Knowledge Graph (KG) is a semantic network that encodes:
  • Entities    – real-world objects (people, places, concepts)
  • Relations   – typed edges between entities
  • Attributes  – key-value properties on entities

Data is stored as RDF triples:   (Subject, Predicate, Object)
  e.g.  (Jodhpur, locatedIn, Rajasthan)
        (Mehrangarh Fort, type, Heritage Site)
        (Mehrangarh Fort, builtBy, Rao Jodha)

KGs support:
  • Inference   – derive new facts via rules (RDFS/OWL)
  • SPARQL      – SQL-like query language for RDF
  • Ontologies  – formal vocabularies (classes, properties)

2. COMPONENTS
─────────────
  Nodes        : Entity URIs or literal values
  Edges        : Predicates (typed relationships)
  Ontology     : Schema (rdfs:subClassOf, owl:equivalentClass …)
  Reasoner     : Infers implicit facts
  Triple Store : Database backend (Blazegraph, Fuseki, Stardog)

3. MAJOR TOOLS
──────────────
  ┌─────────────────────┬──────────────────────────────────────┐
  │ Tool                │ Description                          │
  ├─────────────────────┼──────────────────────────────────────┤
  │ Protégé             │ Free ontology editor (OWL/RDF).      │
  │                     │ Visual class hierarchy, property     │
  │                     │ editors, built-in reasoners (HermiT).│
  ├─────────────────────┼──────────────────────────────────────┤
  │ Apache Jena         │ Java framework: TDB triple store,    │
  │                     │ SPARQL engine, RDFS inference.       │
  ├─────────────────────┼──────────────────────────────────────┤
  │ RDFLib (Python)     │ Pure-Python RDF library. Parses      │
  │                     │ Turtle/N3/JSON-LD; simple SPARQL.   │
  ├─────────────────────┼──────────────────────────────────────┤
  │ Neo4j + Neosemantics│ Property-graph DB with Cypher query  │
  │                     │ language; n10s plugin adds RDF/SPARQL│
  ├─────────────────────┼──────────────────────────────────────┤
  │ Google Knowledge    │ Large-scale commercial KG (~500B     │
  │ Graph / Wikidata    │ triples). Public SPARQL endpoint.    │
  ├─────────────────────┼──────────────────────────────────────┤
  │ OpenLink Virtuoso   │ High-performance triple store;       │
  │                     │ powers DBpedia SPARQL endpoint.      │
  ├─────────────────────┼──────────────────────────────────────┤
  │ NetworkX (Python)   │ General graph library; useful for    │
  │                     │ small KGs, visualisation, analysis.  │
  └─────────────────────┴──────────────────────────────────────┘

4. KG LIFECYCLE
───────────────
  (a) Define Ontology  → choose classes, properties, axioms
  (b) Extract Entities → NER, IE from text / structured data
  (c) Populate Triples → ETL into triple store
  (d) Query & Reason   → SPARQL, OWL inference
  (e) Embed & Learn    → TransE, RoBERTa-KG for downstream ML

5. USE CASES
────────────
  • Semantic search (Google Search panels)
  • Question answering (IBM Watson, Amazon Alexa)
  • Drug interaction graphs (Bio2RDF, UniProt)
  • Fraud detection (link-analysis on financial KGs)
  • Recommendation (Amazon product KG)
"""


# ─────────────────────────────────────────────────────────────
# PART B – HAND-BUILT KNOWLEDGE GRAPH (pure Python, no deps)
# ─────────────────────────────────────────────────────────────

Triple = Tuple[str, str, str]   # (subject, predicate, object)

class KnowledgeGraph:
    """
    Minimal in-memory Knowledge Graph backed by a set of RDF-like triples.

    Supports:
      • add_triple / add_triples
      • query with subject, predicate, and/or object wildcards
      • simple RDFS-style inference (subClassOf, type propagation)
      • entity descriptions
    """

    def __init__(self, name: str = "KG"):
        self.name = name
        self._triples: Set[Triple] = set()

    # ── Mutation ─────────────────────────────────────────────

    def add_triple(self, s: str, p: str, o: str):
        self._triples.add((s, p, o))

    def add_triples(self, triples: List[Triple]):
        for t in triples:
            self.add_triple(*t)

    # ── Query (wildcard = None) ───────────────────────────────

    def query(self, s=None, p=None, o=None) -> List[Triple]:
        """
        Pattern match with optional wildcards.
        query(s="Jodhpur") → all triples where subject is Jodhpur
        query(p="locatedIn") → all location triples
        """
        results = []
        for (ts, tp, to) in self._triples:
            if (s is None or ts == s) and \
               (p is None or tp == p) and \
               (o is None or to == o):
                results.append((ts, tp, to))
        return sorted(results)

    def entities(self) -> Set[str]:
        s_set = {t[0] for t in self._triples}
        o_set = {t[2] for t in self._triples}
        return s_set | o_set

    def describe(self, entity: str) -> Dict[str, List[str]]:
        """Return all predicates and their objects for an entity."""
        desc: Dict[str, List[str]] = {}
        for (s, p, o) in self._triples:
            if s == entity:
                desc.setdefault(p, []).append(o)
        return desc

    # ── RDFS-style inference ──────────────────────────────────

    def infer_subclass_types(self):
        """
        If (A rdf:type C) and (C rdfs:subClassOf D) → infer (A rdf:type D).
        Runs to fixpoint.
        """
        new_triples = set()
        changed = True
        while changed:
            changed = False
            subclass_pairs = [(s, o) for s, p, o in self._triples
                              if p == "rdfs:subClassOf"]
            type_triples    = [(s, o) for s, p, o in self._triples
                               if p == "rdf:type"]
            for entity, klass in type_triples:
                for sub, sup in subclass_pairs:
                    if klass == sub:
                        nt = (entity, "rdf:type", sup)
                        if nt not in self._triples and nt not in new_triples:
                            new_triples.add(nt)
                            changed = True
            self._triples |= new_triples
            new_triples = set()

    def stats(self) -> Dict[str, int]:
        preds = {t[1] for t in self._triples}
        return {
            "triples": len(self._triples),
            "entities": len(self.entities()),
            "predicates": len(preds),
        }

    def to_turtle(self) -> str:
        """Serialise to a simple Turtle-like format for inspection."""
        lines = [f"# Knowledge Graph: {self.name}\n"]
        by_subject: Dict[str, List[Tuple[str,str]]] = {}
        for s, p, o in sorted(self._triples):
            by_subject.setdefault(s, []).append((p, o))
        for subj, pairs in by_subject.items():
            lines.append(f"<{subj}>")
            for p, o in pairs:
                lines.append(f"    {p}  <{o}> ;")
            lines[-1] = lines[-1].rstrip(";") + " ."
            lines.append("")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# PART C – DOMAIN KG: RAJASTHAN TOURISM
# ─────────────────────────────────────────────────────────────

def build_rajasthan_kg() -> KnowledgeGraph:
    """Populate a tourism-domain KG for Rajasthan, India."""
    kg = KnowledgeGraph("Rajasthan Tourism")

    # ── Ontology (class hierarchy) ────────────────────────────
    kg.add_triples([
        ("HeritageMonument", "rdfs:subClassOf", "TouristAttraction"),
        ("Fort",             "rdfs:subClassOf", "HeritageMonument"),
        ("Palace",           "rdfs:subClassOf", "HeritageMonument"),
        ("Temple",           "rdfs:subClassOf", "TouristAttraction"),
        ("WildlifeReserve",  "rdfs:subClassOf", "TouristAttraction"),
        ("City",             "rdfs:subClassOf", "GeographicLocation"),
        ("State",            "rdfs:subClassOf", "GeographicLocation"),
    ])

    # ── Instance triples ──────────────────────────────────────
    kg.add_triples([
        # Places
        ("MehrangarhFort",      "rdf:type",     "Fort"),
        ("MehrangarhFort",      "locatedIn",    "Jodhpur"),
        ("MehrangarhFort",      "builtIn",      "1459"),
        ("MehrangarhFort",      "builtBy",      "RaoJodha"),
        ("MehrangarhFort",      "hasRating",    "4.7"),
        ("MehrangarhFort",      "label",        "Mehrangarh Fort"),

        ("UmaidBhawanPalace",   "rdf:type",     "Palace"),
        ("UmaidBhawanPalace",   "locatedIn",    "Jodhpur"),
        ("UmaidBhawanPalace",   "builtIn",      "1943"),
        ("UmaidBhawanPalace",   "hasRating",    "4.3"),
        ("UmaidBhawanPalace",   "label",        "Umaid Bhawan Palace"),

        ("AmberFort",           "rdf:type",     "Fort"),
        ("AmberFort",           "locatedIn",    "Jaipur"),
        ("AmberFort",           "builtIn",      "1592"),
        ("AmberFort",           "hasRating",    "4.6"),
        ("AmberFort",           "label",        "Amber Fort"),

        ("JaipurCityPalace",    "rdf:type",     "Palace"),
        ("JaipurCityPalace",    "locatedIn",    "Jaipur"),
        ("JaipurCityPalace",    "hasRating",    "4.5"),
        ("JaipurCityPalace",    "label",        "Jaipur City Palace"),

        ("RanthamboreNP",       "rdf:type",     "WildlifeReserve"),
        ("RanthamboreNP",       "locatedIn",    "SawaiMadhopur"),
        ("RanthamboreNP",       "hasAnimal",    "BengalTiger"),
        ("RanthamboreNP",       "hasRating",    "4.6"),
        ("RanthamboreNP",       "label",        "Ranthambore National Park"),

        # Cities
        ("Jodhpur",             "rdf:type",     "City"),
        ("Jodhpur",             "locatedIn",    "Rajasthan"),
        ("Jodhpur",             "knownAs",      "BlueCity"),
        ("Jodhpur",             "label",        "Jodhpur"),

        ("Jaipur",              "rdf:type",     "City"),
        ("Jaipur",              "locatedIn",    "Rajasthan"),
        ("Jaipur",              "knownAs",      "PinkCity"),
        ("Jaipur",              "isCapitalOf",  "Rajasthan"),
        ("Jaipur",              "label",        "Jaipur"),

        ("SawaiMadhopur",       "rdf:type",     "City"),
        ("SawaiMadhopur",       "locatedIn",    "Rajasthan"),

        ("Rajasthan",           "rdf:type",     "State"),
        ("Rajasthan",           "locatedIn",    "India"),
        ("Rajasthan",           "label",        "Rajasthan"),
    ])

    # Apply RDFS inference: Fort/Palace → HeritageMonument → TouristAttraction
    kg.infer_subclass_types()
    return kg


# ─────────────────────────────────────────────────────────────
# PART D – SPARQL-STYLE QUERY EXAMPLES
# ─────────────────────────────────────────────────────────────

def demo_queries(kg: KnowledgeGraph):
    """
    Demonstrate KG query patterns analogous to SPARQL.
    """
    print("\n── Q1: All Forts in the KG ──")
    forts = kg.query(p="rdf:type", o="Fort")
    for t in forts:
        print(f"    {t[0]}")

    print("\n── Q2: Places located in Jodhpur ──")
    in_jod = kg.query(p="locatedIn", o="Jodhpur")
    for t in in_jod:
        print(f"    {t[0]}")

    print("\n── Q3: All TouristAttractions (after inference) ──")
    attractions = kg.query(p="rdf:type", o="TouristAttraction")
    for t in attractions:
        print(f"    {t[0]}")

    print("\n── Q4: Describe MehrangarhFort ──")
    desc = kg.describe("MehrangarhFort")
    for pred, vals in desc.items():
        print(f"    {pred:25s} → {', '.join(vals)}")

    print("\n── Q5: Which city is the capital of Rajasthan? ──")
    cap = kg.query(p="isCapitalOf", o="Rajasthan")
    for t in cap:
        print(f"    {t[0]}")

    print("\n── KG Statistics ──")
    for k, v in kg.stats().items():
        print(f"    {k}: {v}")


if __name__ == "__main__":
    print(KG_OVERVIEW)
    kg = build_rajasthan_kg()
    print("Knowledge Graph built successfully.")
    demo_queries(kg)
    print("\n── Turtle Serialisation (excerpt) ──")
    ttl = kg.to_turtle()
    # Print first 40 lines
    for line in ttl.split("\n")[:40]:
        print(line)
