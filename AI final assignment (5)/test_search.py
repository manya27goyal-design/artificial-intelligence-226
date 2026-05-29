"""
Test Cases for Assignment 1: Search Algorithms
================================================
Covers Minimax, Alpha-Beta, Heuristic Alpha-Beta, and MCTS.

Run:  python test_search.py
"""

import math
import time
import random
import sys
sys.path.insert(0, '.')
from search_algorithms import (
    TicTacToe, MinimaxAgent, AlphaBetaAgent,
    HeuristicAlphaBetaAgent, MCTSAgent
)

PASS = "✓ PASS"
FAIL = "✗ FAIL"
results = []

def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((name, condition))
    print(f"  {status}  {name}", f"({detail})" if detail else "")

def play_game(agent_x, agent_o):
    game = TicTacToe()
    while not game.is_terminal():
        if game.current_player == 1:
            move, _ = agent_x.best_move(game)
        else:
            move, _ = agent_o.best_move(game)
        game.make_move(move)
    return game.result()

# ─────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 1: TicTacToe Game Engine")
print("="*60)

g = TicTacToe()
check("Empty board has 9 legal moves", len(g.legal_moves()) == 9)
check("No winner on empty board", g.winner() == 0)
check("Empty board not terminal", not g.is_terminal())

g.make_move(0); g.make_move(3); g.make_move(1); g.make_move(4); g.make_move(2)
check("X wins row 0 (cells 0,1,2)", g.winner() == 1, f"winner={g.winner()}")
check("Terminal after X wins", g.is_terminal())

g2 = TicTacToe()
for m in [0,1,2,3,5,4,6,8,7]: g2.make_move(m)
check("Draw game: 0 legal moves", len(g2.legal_moves()) == 0)
check("Draw game: winner == 0", g2.winner() == 0)
check("Draw game: is_terminal", g2.is_terminal())

# ─────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 2: Minimax Search")
print("="*60)

mm = MinimaxAgent()
g = TicTacToe()
for m in [0, 3, 1, 4]: g.make_move(m)  # X needs 2 to win
move, val = mm.best_move(g)
check("Minimax finds winning move for X", move == 2, f"move={move}, val={val}")

# O's turn, O has 3,4 and needs 5 to win row
g = TicTacToe()
g.make_move(0); g.make_move(3); g.make_move(6); g.make_move(4); g.make_move(8)
move, val = mm.best_move(g)
check("Minimax finds winning move for O", move == 5, f"move={move}, val={val}")

g = TicTacToe()
move, val = mm.best_move(g)
check("Minimax value from start is 0 (draw with perfect play)", val == 0, f"val={val}")
check("Minimax explored > 0 nodes", mm.nodes_explored > 0, f"nodes={mm.nodes_explored}")

result = play_game(MinimaxAgent(), MinimaxAgent())
check("Minimax vs Minimax always draws", result == 0, f"result={result}")

# ─────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 3: Alpha-Beta Pruning")
print("="*60)

ab = AlphaBetaAgent()
g = TicTacToe()
for m in [0, 3, 1, 4]: g.make_move(m)
move, val = ab.best_move(g)
check("Alpha-Beta finds winning move for X", move == 2, f"move={move}")

g = TicTacToe()
move_ab, val_ab = ab.best_move(g)
check("Alpha-Beta value from start == 0", val_ab == 0, f"val={val_ab}")

mm2 = MinimaxAgent(); ab2 = AlphaBetaAgent()
mm2.best_move(TicTacToe()); ab2.best_move(TicTacToe())
check("Alpha-Beta prunes: fewer nodes than Minimax",
      ab2.nodes_explored < mm2.nodes_explored,
      f"AB={ab2.nodes_explored}, MM={mm2.nodes_explored}")
check("Alpha-Beta pruned at least one branch", ab2.nodes_pruned > 0,
      f"pruned={ab2.nodes_pruned}")

g3 = TicTacToe()
for m in [4, 0, 2, 6]: g3.make_move(m)
m_mm, v_mm = MinimaxAgent().best_move(g3)
m_ab, v_ab = AlphaBetaAgent().best_move(g3)
check("Alpha-Beta agrees with Minimax on best value", v_mm == v_ab,
      f"MM={v_mm}, AB={v_ab}")

result = play_game(AlphaBetaAgent(), AlphaBetaAgent())
check("Alpha-Beta vs Alpha-Beta always draws", result == 0)

# ─────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 4: Heuristic Alpha-Beta")
print("="*60)

hab = HeuristicAlphaBetaAgent(max_depth=9)
g = TicTacToe()
for m in [0, 3, 1, 4]: g.make_move(m)
move, val = hab.best_move(g)
check("Heuristic AB (depth=9) finds X's winning move", move == 2, f"move={move}")

hab_shallow = HeuristicAlphaBetaAgent(max_depth=2)
g = TicTacToe()
move, val = hab_shallow.best_move(g)
check("Heuristic AB (depth=2) returns valid move", move in range(9), f"move={move}")

g_empty = TicTacToe()
check("Heuristic evaluate empty board == 0", g_empty.evaluate() == 0)

g_xwin = TicTacToe()
for m in [0,3,1,4,2]: g_xwin.make_move(m)
check("Heuristic evaluate X-win board positive", g_xwin.evaluate() > 0,
      f"val={g_xwin.evaluate()}")

move_h, _ = HeuristicAlphaBetaAgent(max_depth=9).best_move(TicTacToe())
check("Heuristic AB (full depth) starts at centre", move_h == 4, f"move={move_h}")

result = play_game(HeuristicAlphaBetaAgent(max_depth=9),
                   HeuristicAlphaBetaAgent(max_depth=9))
check("Heuristic AB vs Heuristic AB draws with full depth", result == 0)

# ─────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 5: Monte-Carlo Tree Search")
print("="*60)

random.seed(42)
mcts = MCTSAgent(iterations=2000)

# X wins immediately (move 2)
g = TicTacToe()
for m in [0, 3, 1, 4]: g.make_move(m)
move, wr = mcts.best_move(g)
check("MCTS finds X's immediate win at 2", move == 2, f"move={move}, win_rate={wr:.2f}")

# O wins immediately (move 5): board [1,0,0,-1,-1,0,1,0,1], O to play
g = TicTacToe()
g.make_move(0); g.make_move(3); g.make_move(6); g.make_move(4); g.make_move(8)
move, wr = mcts.best_move(g)
check("MCTS finds O's immediate win at 5", move == 5, f"move={move}, win_rate={wr:.2f}")

# X blocks O's immediate win: O has 6,7; X must play 8
g2 = TicTacToe()
g2.make_move(0); g2.make_move(6); g2.make_move(4); g2.make_move(7)
move2, _ = MCTSAgent(iterations=3000).best_move(g2)
check("MCTS blocks O's diagonal threat at 8", move2 == 8, f"move={move2}")

# Fresh board: returns legal move
move_mcts, _ = MCTSAgent(iterations=500).best_move(TicTacToe())
check("MCTS returns legal move on fresh board", move_mcts in range(9), f"move={move_mcts}")

_, wr = MCTSAgent(iterations=500).best_move(TicTacToe())
check("MCTS win rate in [0,1]", 0 <= wr <= 1, f"win_rate={wr:.3f}")

wins_mcts, draws, wins_mm = 0, 0, 0
for seed in range(10):
    random.seed(seed)
    r = play_game(MCTSAgent(iterations=500), MinimaxAgent())
    if r == 1: wins_mcts += 1
    elif r == 0: draws += 1
    else: wins_mm += 1
check("MCTS vs Minimax: does not lose every game",
      wins_mm < 10, f"MCTS_wins={wins_mcts}, draws={draws}, MM_wins={wins_mm}")

# ─────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 6: Performance Benchmarks")
print("="*60)

algorithms = [
    ("Minimax",           MinimaxAgent(),              lambda a,g: a.best_move(g)),
    ("Alpha-Beta",        AlphaBetaAgent(),            lambda a,g: a.best_move(g)),
    ("Heuristic AB d=4",  HeuristicAlphaBetaAgent(4),  lambda a,g: a.best_move(g)),
    ("MCTS 500 iters",    MCTSAgent(500),               lambda a,g: a.best_move(g)),
]

print(f"\n  {'Algorithm':<20} {'Time(ms)':>10} {'Nodes/Iters':>15}")
print(f"  {'-'*20} {'-'*10} {'-'*15}")
for name, agent, fn in algorithms:
    t0 = time.perf_counter()
    fn(agent, TicTacToe())
    elapsed = (time.perf_counter() - t0) * 1000
    detail = getattr(agent, 'nodes_explored', None) or getattr(agent, 'iterations', '—')
    print(f"  {name:<20} {elapsed:>10.2f} {str(detail):>15}")

# ─────────────────────────────────────────────
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
    print("\n  Failed tests:")
    for name, ok in results:
        if not ok:
            print(f"    - {name}")
