"""
Test Cases for Assignment 4: Bayesian Networks
Run:  python test_bayesian.py
"""
import sys
sys.path.insert(0, '.')
from bayesian_network import (
    Node, BayesianNetwork, build_chest_disease_bn
)

PASS = "✓ PASS"; FAIL = "✗ FAIL"
results = []
EPS = 1e-6

def check(name, cond, detail=""):
    status = PASS if cond else FAIL
    results.append((name, cond))
    print(f"  {status}  {name}", f"({detail})" if detail else "")

def approx_eq(a, b, tol=1e-4):
    return abs(a - b) < tol

# ─── Simple 2-node network ────────────────────────────────────
print("\n" + "="*60)
print("SECTION 1: Minimal BN (Rain → Wet)")
print("="*60)

bn = BayesianNetwork("Rain")
bn.add_node(Node("Rain", ["yes","no"], [],
                 {(): {"yes": 0.3, "no": 0.7}}))
bn.add_node(Node("Wet", ["yes","no"], ["Rain"],
                 {("yes",): {"yes": 0.9, "no": 0.1},
                  ("no",):  {"yes": 0.2, "no": 0.8}}))

check("P(Rain=yes) ≈ 0.3", approx_eq(bn.prior("Rain")["yes"], 0.3),
      f"{bn.prior('Rain')['yes']:.4f}")

# P(Wet=yes) = P(Wet|Rain=yes)*P(Rain=yes) + P(Wet|Rain=no)*P(Rain=no)
#            = 0.9*0.3 + 0.2*0.7 = 0.27 + 0.14 = 0.41
prior_wet = bn.prior("Wet")["yes"]
check("P(Wet=yes) ≈ 0.41", approx_eq(prior_wet, 0.41), f"{prior_wet:.4f}")

# With Rain=yes, P(Wet=yes) = 0.9
p_wet_given_rain = bn.query("Wet", {"Rain":"yes"})["yes"]
check("P(Wet=yes|Rain=yes) = 0.9", approx_eq(p_wet_given_rain, 0.9),
      f"{p_wet_given_rain:.4f}")

# With Rain=no, P(Wet=yes) = 0.2
p_wet_no_rain = bn.query("Wet", {"Rain":"no"})["yes"]
check("P(Wet=yes|Rain=no) = 0.2", approx_eq(p_wet_no_rain, 0.2),
      f"{p_wet_no_rain:.4f}")

# Posterior sums to 1
dist = bn.query("Rain", {"Wet":"yes"})
check("Posterior P(Rain|Wet=yes) sums to 1",
      approx_eq(sum(dist.values()), 1.0), f"{sum(dist.values()):.6f}")

# Bayes' theorem check: P(Rain=yes|Wet=yes) = P(Wet=yes|Rain=yes)*P(Rain=yes)/P(Wet=yes)
expected = (0.9 * 0.3) / 0.41
check("P(Rain=yes|Wet=yes) matches Bayes theorem",
      approx_eq(dist["yes"], expected), f"got={dist['yes']:.4f}, expected={expected:.4f}")

# Joint probability
jp = bn.joint_probability({"Rain":"yes","Wet":"yes"})
check("Joint P(Rain=yes,Wet=yes) = 0.27", approx_eq(jp, 0.27), f"{jp:.4f}")

# MAP query
state, prob = bn.map_query("Wet", {"Rain":"yes"})
check("MAP(Wet|Rain=yes) = yes", state == "yes", f"state={state}")

# ─── Chest Disease Network ───────────────────────────────────
print("\n" + "="*60)
print("SECTION 2: Chest Disease BN")
print("="*60)

cd = build_chest_disease_bn()

check("Network has 8 nodes", len(cd._nodes) == 8)

# Prior probabilities (prior Lung Cancer ≈ 0.055)
# P(LC=yes) = P(LC|S=yes)*P(S=yes) + P(LC|S=no)*P(S=no)
#           = 0.10*0.5 + 0.01*0.5 = 0.055
p_lc = cd.prior("Lung_Cancer")["yes"]
check("P(Lung_Cancer=yes) ≈ 0.055", approx_eq(p_lc, 0.055, tol=0.001),
      f"{p_lc:.4f}")

# Smoking increases lung cancer probability
p_lc_smoker  = cd.query("Lung_Cancer", {"Smoking":"yes"})["yes"]
p_lc_nonsmoker = cd.query("Lung_Cancer", {"Smoking":"no"})["yes"]
check("P(LC|Smoking=yes) > P(LC|Smoking=no)",
      p_lc_smoker > p_lc_nonsmoker,
      f"smoker={p_lc_smoker:.4f}, non={p_lc_nonsmoker:.4f}")
check("P(LC|Smoking=yes) = 0.10", approx_eq(p_lc_smoker, 0.10), f"{p_lc_smoker:.4f}")

# Visit Asia increases TB probability
p_tb_asia    = cd.query("Tuberculosis", {"Visit_Asia":"yes"})["yes"]
p_tb_no_asia = cd.query("Tuberculosis", {"Visit_Asia":"no"})["yes"]
check("P(TB|Asia=yes) > P(TB|Asia=no)",
      p_tb_asia > p_tb_no_asia,
      f"asia={p_tb_asia:.4f}, no_asia={p_tb_no_asia:.4f}")

# Positive X-ray strongly raises cancer probability
p_lc_xray_pos = cd.query("Lung_Cancer", {"XRay":"positive"})["yes"]
check("Positive X-ray raises P(Lung_Cancer)",
      p_lc_xray_pos > p_lc,
      f"prior={p_lc:.4f}, with_xray={p_lc_xray_pos:.4f}")

# Dyspnoea + X-ray positive: diagnose more strongly
p_lc_dys_xray = cd.query("Lung_Cancer",
                          {"Dyspnoea":"yes","XRay":"positive"})["yes"]
check("Dyspnoea+XRay+ raises P(LC) further vs XRay+ alone",
      p_lc_dys_xray >= p_lc_xray_pos,
      f"with_both={p_lc_dys_xray:.4f}, xray_only={p_lc_xray_pos:.4f}")

# All posteriors sum to 1
for target in cd._nodes:
    dist = cd.prior(target)
    check(f"Prior of {target} sums to 1",
          approx_eq(sum(dist.values()), 1.0), f"{sum(dist.values()):.6f}")

# ─── 3-node chain: Explaining Away ───────────────────────────
print("\n" + "="*60)
print("SECTION 3: Explaining Away (Burglar-Alarm network)")
print("="*60)

ba = BayesianNetwork("BurglarAlarm")
ba.add_node(Node("Burglary", ["yes","no"], [],
                 {(): {"yes":0.001,"no":0.999}}))
ba.add_node(Node("Earthquake", ["yes","no"], [],
                 {(): {"yes":0.002,"no":0.998}}))
ba.add_node(Node("Alarm", ["yes","no"],
                 ["Burglary","Earthquake"],
                 {("yes","yes"): {"yes":0.95,"no":0.05},
                  ("yes","no"):  {"yes":0.94,"no":0.06},
                  ("no","yes"):  {"yes":0.29,"no":0.71},
                  ("no","no"):   {"yes":0.001,"no":0.999}}))

# Alarm=yes raises Burglary probability
p_b_prior = ba.prior("Burglary")["yes"]
p_b_alarm = ba.query("Burglary", {"Alarm":"yes"})["yes"]
check("Alarm=yes raises P(Burglary)", p_b_alarm > p_b_prior,
      f"prior={p_b_prior:.5f}, posterior={p_b_alarm:.4f}")

# Explaining away: given Alarm=yes AND Earthquake=yes, Burglary becomes less likely
p_b_alarm_eq = ba.query("Burglary", {"Alarm":"yes","Earthquake":"yes"})["yes"]
check("Earthquake explains away Alarm (Burglary decreases)",
      p_b_alarm_eq < p_b_alarm,
      f"alarm_only={p_b_alarm:.4f}, +earthquake={p_b_alarm_eq:.4f}")

# All posteriors sum to 1
for target in ["Burglary","Earthquake","Alarm"]:
    dist = ba.prior(target)
    check(f"Prior of {target} sums to 1",
          approx_eq(sum(dist.values()), 1.0))

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
