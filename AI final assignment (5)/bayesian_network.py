"""
Assignment 4: Bayesian Networks — Tools & Implementation
=========================================================
Explores tools for Bayesian Network modelling, problem representation,
and probabilistic inference.

Example chosen: Medical Diagnosis — Chest Disease Network
  (classic Asia / Chest-Clinic network, simplified)

  Variables:
    Visit_Asia  (A) : Did the patient visit Asia recently?
    Tuberculosis(T) : Has the patient tuberculosis?
    Smoking     (S) : Does the patient smoke?
    Lung_Cancer (L) : Does the patient have lung cancer?
    Bronchitis  (B) : Does the patient have bronchitis?
    TbOrCancer  (E) : Either Tuberculosis or Lung Cancer (deterministic OR)
    X_Ray       (X) : Is the X-ray positive?
    Dyspnoea    (D) : Does the patient have dyspnoea (breathlessness)?

  Directed edges (parent → child):
    A → T,  S → L,  S → B,  T → E,  L → E,  E → X,  E → D,  B → D

Author: AI Assignments
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


# ─────────────────────────────────────────────────────────────
# TOOL SURVEY (printed overview)
# ─────────────────────────────────────────────────────────────

TOOL_SURVEY = """
╔══════════════════════════════════════════════════════════════╗
║        BAYESIAN NETWORK TOOLS — SURVEY                      ║
╚══════════════════════════════════════════════════════════════╝

WHAT IS A BAYESIAN NETWORK?
────────────────────────────
A Bayesian Network (BN) is a probabilistic graphical model (DAG)
where:
  • Nodes  → random variables (discrete or continuous)
  • Edges  → direct probabilistic dependencies (parent → child)
  • Each node stores a Conditional Probability Table (CPT):
      P(Node | Parents)

BNs satisfy the Markov condition: each node is conditionally
independent of its non-descendants given its parents.

Joint probability factorises as:
  P(X1,…,Xn) = Π  P(Xi | Parents(Xi))

INFERENCE TYPES:
  • Prior inference    : P(X) with no evidence
  • Posterior inference: P(X | evidence) via Bayes' theorem
  • MAP estimation     : most probable explanation
  • Causal reasoning   : interventions (do-calculus)

MAJOR TOOLS:
────────────
┌────────────────────┬─────────────────────────────────────────┐
│ Tool               │ Description                             │
├────────────────────┼─────────────────────────────────────────┤
│ pgmpy (Python)     │ Full-featured BN library. Supports      │
│                    │ exact (VE, BF) and approx (MCMC, LW)    │
│                    │ inference; structure learning; BIF/XML.  │
├────────────────────┼─────────────────────────────────────────┤
│ pomegranate (Py)   │ GPU-accelerated; HMMs, GMMs, BNs.       │
│                    │ Good for large-scale ML pipelines.      │
├────────────────────┼─────────────────────────────────────────┤
│ Netica             │ Commercial GUI tool; widely used in     │
│                    │ risk analysis and medical decision.     │
├────────────────────┼─────────────────────────────────────────┤
│ Hugin Expert       │ Commercial; junction tree inference;    │
│                    │ used in oil, finance, healthcare.       │
├────────────────────┼─────────────────────────────────────────┤
│ GeNIe / SMILE      │ Free academic tool (U. Pittsburgh);     │
│                    │ drag-and-drop BN editor + inference.    │
├────────────────────┼─────────────────────────────────────────┤
│ BayesiaLab         │ Commercial; unsupervised structure      │
│                    │ learning; market research / causal AI.  │
├────────────────────┼─────────────────────────────────────────┤
│ Stan / PyMC        │ Full probabilistic programming;         │
│                    │ MCMC/NUTS sampling; continuous BNs.     │
├────────────────────┼─────────────────────────────────────────┤
│ bnlearn (R)        │ R package; PC, GES, TABU structure       │
│                    │ learning; graphviz visualisation.       │
└────────────────────┴─────────────────────────────────────────┘

INFERENCE ALGORITHMS:
  Variable Elimination (VE)  – exact; eliminates variables one-by-one
  Junction Tree / Belief Prop – exact; efficient for tree-width graphs
  Likelihood Weighting (LW)  – approx; importance sampling
  Gibbs Sampling (MCMC)      – approx; Markov chain simulation
"""


# ─────────────────────────────────────────────────────────────
# BAYESIAN NETWORK IMPLEMENTATION (pure Python, no deps)
# ─────────────────────────────────────────────────────────────

@dataclass
class Node:
    """
    A node in the Bayesian Network.

    Attributes:
        name    : Variable name
        states  : Possible values, e.g. ['yes','no'] or [True,False]
        parents : List of parent node names (ordered)
        cpt     : Conditional Probability Table as a dict
                  Key  = tuple of parent state values (or () if no parents)
                  Value= dict mapping this node's state → probability
    """
    name: str
    states: List[str]
    parents: List[str]
    cpt: Dict[Tuple, Dict[str, float]]


class BayesianNetwork:
    """
    Discrete Bayesian Network with exact inference via
    Variable Elimination.

    Interface:
        add_node(node)                   – add a Node to the network
        query(target, evidence)          – P(target | evidence)
        joint_probability(assignment)    – P(X1=x1, …, Xn=xn)
    """

    def __init__(self, name: str = "BN"):
        self.name = name
        self._nodes: Dict[str, Node] = {}
        self._order: List[str] = []      # topological insertion order

    def add_node(self, node: Node):
        self._nodes[node.name] = node
        self._order.append(node.name)

    # ── CPT lookup ───────────────────────────────────────────

    def _lookup(self, node: Node, parent_vals: Tuple, state: str) -> float:
        """Fetch P(node=state | parent_vals) from CPT."""
        return node.cpt[parent_vals][state]

    def _parent_values(self, node: Node, assignment: Dict[str, str]) -> Tuple:
        return tuple(assignment[p] for p in node.parents)

    # ── Joint probability ─────────────────────────────────────

    def joint_probability(self, assignment: Dict[str, str]) -> float:
        """
        Compute the joint probability of a complete assignment.
        P(x1,…,xn) = Π P(xi | parents(xi))
        """
        prob = 1.0
        for name, node in self._nodes.items():
            pv = self._parent_values(node, assignment)
            prob *= self._lookup(node, pv, assignment[name])
        return prob

    # ── Variable Elimination (Exact Inference) ────────────────

    def query(self, target: str, evidence: Dict[str, str]) -> Dict[str, float]:
        """
        Compute P(target | evidence) using Variable Elimination.

        Algorithm:
          1. Enumerate all complete assignments consistent with evidence.
          2. Sum joint probabilities for each value of target (marginalise).
          3. Normalise.

        This brute-force enumeration is exact and correct but
        exponential in the number of variables (fine for small BNs).
        """
        target_node = self._nodes[target]
        hidden_vars = [n for n in self._order
                       if n != target and n not in evidence]

        # Collect all possible states for hidden variables + target
        all_vars = [target] + hidden_vars
        all_states = {v: self._nodes[v].states for v in all_vars}

        # Enumerate assignments
        result = {s: 0.0 for s in target_node.states}

        def enumerate_all(variables, partial):
            if not variables:
                jp = self.joint_probability(partial)
                result[partial[target]] += jp
                return
            var = variables[0]
            rest = variables[1:]
            for s in all_states[var]:
                enumerate_all(rest, {**partial, var: s})

        enumerate_all(all_vars, dict(evidence))

        # Normalise
        total = sum(result.values())
        if total == 0:
            return result
        return {k: v / total for k, v in result.items()}

    def map_query(self, target: str, evidence: Dict[str, str]) -> Tuple[str, float]:
        """Return the most probable state for target given evidence."""
        dist = self.query(target, evidence)
        best = max(dist, key=dist.get)
        return best, dist[best]

    # ── Prior marginal ────────────────────────────────────────

    def prior(self, target: str) -> Dict[str, float]:
        """P(target) with no evidence."""
        return self.query(target, {})

    def __repr__(self):
        return f"BayesianNetwork('{self.name}', nodes={list(self._nodes.keys())})"


# ─────────────────────────────────────────────────────────────
# CHEST-DISEASE EXAMPLE NETWORK
# ─────────────────────────────────────────────────────────────
# CPT probabilities adapted from the classic Asia network
# (Lauritzen & Spiegelhalter 1988).

def build_chest_disease_bn() -> BayesianNetwork:
    """
    Build and return the chest disease Bayesian Network.

    Structure:
      Visit_Asia → Tuberculosis
      Smoking → Lung_Cancer
      Smoking → Bronchitis
      Tuberculosis → TbOrCancer
      Lung_Cancer  → TbOrCancer
      TbOrCancer   → XRay
      TbOrCancer   → Dyspnoea
      Bronchitis   → Dyspnoea
    """
    bn = BayesianNetwork("Chest Disease Diagnosis")

    # ── P(Visit_Asia) ─────────────────────────────────────────
    bn.add_node(Node(
        name="Visit_Asia", states=["yes","no"], parents=[],
        cpt={(): {"yes": 0.01, "no": 0.99}}
    ))

    # ── P(Tuberculosis | Visit_Asia) ──────────────────────────
    bn.add_node(Node(
        name="Tuberculosis", states=["yes","no"],
        parents=["Visit_Asia"],
        cpt={
            ("yes",): {"yes": 0.05, "no": 0.95},
            ("no",):  {"yes": 0.01, "no": 0.99},
        }
    ))

    # ── P(Smoking) ────────────────────────────────────────────
    bn.add_node(Node(
        name="Smoking", states=["yes","no"], parents=[],
        cpt={(): {"yes": 0.50, "no": 0.50}}
    ))

    # ── P(Lung_Cancer | Smoking) ──────────────────────────────
    bn.add_node(Node(
        name="Lung_Cancer", states=["yes","no"],
        parents=["Smoking"],
        cpt={
            ("yes",): {"yes": 0.10, "no": 0.90},
            ("no",):  {"yes": 0.01, "no": 0.99},
        }
    ))

    # ── P(Bronchitis | Smoking) ───────────────────────────────
    bn.add_node(Node(
        name="Bronchitis", states=["yes","no"],
        parents=["Smoking"],
        cpt={
            ("yes",): {"yes": 0.60, "no": 0.40},
            ("no",):  {"yes": 0.30, "no": 0.70},
        }
    ))

    # ── P(TbOrCancer | Tuberculosis, Lung_Cancer) ────────────
    # Deterministic OR: yes if either parent is yes
    bn.add_node(Node(
        name="TbOrCancer", states=["yes","no"],
        parents=["Tuberculosis", "Lung_Cancer"],
        cpt={
            ("yes","yes"): {"yes": 1.0, "no": 0.0},
            ("yes","no"):  {"yes": 1.0, "no": 0.0},
            ("no","yes"):  {"yes": 1.0, "no": 0.0},
            ("no","no"):   {"yes": 0.0, "no": 1.0},
        }
    ))

    # ── P(XRay | TbOrCancer) ──────────────────────────────────
    bn.add_node(Node(
        name="XRay", states=["positive","negative"],
        parents=["TbOrCancer"],
        cpt={
            ("yes",): {"positive": 0.98, "negative": 0.02},
            ("no",):  {"positive": 0.05, "negative": 0.95},
        }
    ))

    # ── P(Dyspnoea | TbOrCancer, Bronchitis) ──────────────────
    bn.add_node(Node(
        name="Dyspnoea", states=["yes","no"],
        parents=["TbOrCancer", "Bronchitis"],
        cpt={
            ("yes","yes"): {"yes": 0.90, "no": 0.10},
            ("yes","no"):  {"yes": 0.70, "no": 0.30},
            ("no","yes"):  {"yes": 0.80, "no": 0.20},
            ("no","no"):   {"yes": 0.10, "no": 0.90},
        }
    ))

    return bn


# ─────────────────────────────────────────────────────────────
# DEMONSTRATION
# ─────────────────────────────────────────────────────────────

def run_demo():
    print(TOOL_SURVEY)
    bn = build_chest_disease_bn()
    print(f"\nNetwork: {bn}\n")

    scenarios = [
        ("Prior probability of Lung Cancer",
         "Lung_Cancer", {}),
        ("P(Lung Cancer | Smoking=yes)",
         "Lung_Cancer", {"Smoking": "yes"}),
        ("P(Tuberculosis | Visit_Asia=yes)",
         "Tuberculosis", {"Visit_Asia": "yes"}),
        ("P(Dyspnoea | XRay=positive, Smoking=yes)",
         "Dyspnoea", {"XRay": "positive", "Smoking": "yes"}),
        ("P(Smoking | Dyspnoea=yes) — explaining-away",
         "Smoking", {"Dyspnoea": "yes"}),
        ("P(Lung_Cancer | Dyspnoea=yes, XRay=positive)",
         "Lung_Cancer", {"Dyspnoea": "yes", "XRay": "positive"}),
    ]

    print("─" * 60)
    for desc, target, evidence in scenarios:
        dist = bn.query(target, evidence)
        print(f"\n{desc}")
        ev_str = ", ".join(f"{k}={v}" for k,v in evidence.items()) or "∅"
        print(f"  Evidence : {ev_str}")
        for state, prob in dist.items():
            bar = "█" * int(prob * 30)
            print(f"  P({target}={state:8s}) = {prob:.4f}  {bar}")
    print("\n" + "─" * 60)


if __name__ == "__main__":
    run_demo()
