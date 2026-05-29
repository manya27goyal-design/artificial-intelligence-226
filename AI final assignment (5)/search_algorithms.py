"""
Assignment 1: Game Search Algorithms
======================================
Implements:
  1. Minimax Search
  2. Alpha-Beta Pruning Search
  3. Heuristic Alpha-Beta Search (depth-limited with evaluation function)
  4. Monte-Carlo Tree Search (MCTS)

All algorithms are demonstrated on a Tic-Tac-Toe game.

Author: AI Assignments
"""

import math
import random
import time
from copy import deepcopy
from collections import defaultdict


# ─────────────────────────────────────────────
# TIC-TAC-TOE GAME ENGINE
# ─────────────────────────────────────────────

class TicTacToe:
    """
    A standard 3×3 Tic-Tac-Toe board.

    Convention:
        +1  → 'X' (Maximiser)
        -1  → 'O' (Minimiser)
         0  → empty cell
    """

    def __init__(self):
        self.board = [0] * 9          # flat index: row*3 + col
        self.current_player = 1       # X starts

    # ── Board utilities ──────────────────────

    def clone(self):
        g = TicTacToe()
        g.board = self.board[:]
        g.current_player = self.current_player
        return g

    def legal_moves(self):
        return [i for i, v in enumerate(self.board) if v == 0]

    def make_move(self, idx):
        assert self.board[idx] == 0, "Cell already occupied"
        self.board[idx] = self.current_player
        self.current_player *= -1

    def undo_move(self, idx):
        self.board[idx] = 0
        self.current_player *= -1

    def winner(self):
        """Return +1, -1, or 0 (no winner yet)."""
        lines = [
            (0,1,2),(3,4,5),(6,7,8),   # rows
            (0,3,6),(1,4,7),(2,5,8),   # cols
            (0,4,8),(2,4,6)            # diags
        ]
        for a,b,c in lines:
            if self.board[a] == self.board[b] == self.board[c] != 0:
                return self.board[a]
        return 0

    def is_terminal(self):
        return self.winner() != 0 or len(self.legal_moves()) == 0

    def result(self):
        """Terminal utility: +1 X wins, -1 O wins, 0 draw."""
        return self.winner()

    def display(self):
        sym = {1:'X', -1:'O', 0:'.'}
        for row in range(3):
            print(' '.join(sym[self.board[row*3+col]] for col in range(3)))
        print()

    # ── Heuristic evaluation (for depth-limited search) ──────────────────

    def evaluate(self):
        """
        Static board evaluation from X's perspective.

        Score lines that are still 'open' (no mix of X and O):
          3-in-a-row X  →  +100
          2-in-a-row X  →  +10
          1-in-a-row X  →  +1
          Mirror negatives for O.
        """
        w = self.winner()
        if w == 1:
            return 100
        if w == -1:
            return -100

        lines = [
            (0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)
        ]
        score = 0
        for a,b,c in lines:
            vals = [self.board[a], self.board[b], self.board[c]]
            xs = vals.count(1)
            os = vals.count(-1)
            if xs > 0 and os > 0:
                continue          # blocked line – worthless
            if xs == 3:
                score += 100
            elif xs == 2:
                score += 10
            elif xs == 1:
                score += 1
            if os == 3:
                score -= 100
            elif os == 2:
                score -= 10
            elif os == 1:
                score -= 1
        return score


# ─────────────────────────────────────────────
# 1. MINIMAX SEARCH
# ─────────────────────────────────────────────

class MinimaxAgent:
    """
    Classic Minimax search.

    • Explores the full game tree to the terminal nodes.
    • MAX player (X, +1) tries to maximise; MIN player (O, -1) minimises.
    • Returns the best move for the current player.

    Complexity: O(b^d) where b = branching factor, d = depth.
    """

    def __init__(self):
        self.nodes_explored = 0

    def minimax(self, game, is_maximising):
        self.nodes_explored += 1

        if game.is_terminal():
            return game.result()

        moves = game.legal_moves()

        if is_maximising:
            best = -math.inf
            for m in moves:
                game.make_move(m)
                val = self.minimax(game, False)
                game.undo_move(m)
                best = max(best, val)
            return best
        else:
            best = math.inf
            for m in moves:
                game.make_move(m)
                val = self.minimax(game, True)
                game.undo_move(m)
                best = min(best, val)
            return best

    def best_move(self, game):
        self.nodes_explored = 0
        best_val = -math.inf if game.current_player == 1 else math.inf
        best_m = None
        is_max = (game.current_player == 1)

        for m in game.legal_moves():
            game.make_move(m)
            val = self.minimax(game, not is_max)
            game.undo_move(m)

            if is_max and val > best_val:
                best_val, best_m = val, m
            elif not is_max and val < best_val:
                best_val, best_m = val, m

        return best_m, best_val


# ─────────────────────────────────────────────
# 2. ALPHA-BETA PRUNING SEARCH
# ─────────────────────────────────────────────

class AlphaBetaAgent:
    """
    Alpha-Beta Pruning – prunes branches that cannot affect the outcome.

    • Alpha: best already ensured for MAX along the path.
    • Beta:  best already ensured for MIN along the path.
    • A branch is pruned when alpha >= beta (β-cutoff for MAX, α-cutoff for MIN).

    Worst-case: O(b^d). Best-case (perfect ordering): O(b^(d/2)).
    """

    def __init__(self):
        self.nodes_explored = 0
        self.nodes_pruned = 0

    def alpha_beta(self, game, alpha, beta, is_maximising):
        self.nodes_explored += 1

        if game.is_terminal():
            return game.result()

        if is_maximising:
            value = -math.inf
            for m in game.legal_moves():
                game.make_move(m)
                value = max(value, self.alpha_beta(game, alpha, beta, False))
                game.undo_move(m)
                alpha = max(alpha, value)
                if alpha >= beta:
                    self.nodes_pruned += 1
                    break          # β-cutoff
            return value
        else:
            value = math.inf
            for m in game.legal_moves():
                game.make_move(m)
                value = min(value, self.alpha_beta(game, alpha, beta, True))
                game.undo_move(m)
                beta = min(beta, value)
                if alpha >= beta:
                    self.nodes_pruned += 1
                    break          # α-cutoff
            return value

    def best_move(self, game):
        self.nodes_explored = 0
        self.nodes_pruned = 0
        is_max = (game.current_player == 1)
        best_val = -math.inf if is_max else math.inf
        best_m = None

        for m in game.legal_moves():
            game.make_move(m)
            val = self.alpha_beta(game, -math.inf, math.inf, not is_max)
            game.undo_move(m)

            if is_max and val > best_val:
                best_val, best_m = val, m
            elif not is_max and val < best_val:
                best_val, best_m = val, m

        return best_m, best_val


# ─────────────────────────────────────────────
# 3. HEURISTIC ALPHA-BETA SEARCH
# ─────────────────────────────────────────────

class HeuristicAlphaBetaAgent:
    """
    Depth-limited Alpha-Beta with a static heuristic evaluation function.

    • Identical to Alpha-Beta but the recursion stops at a fixed depth.
    • At the cutoff depth the static evaluator scores the position.
    • Move ordering (centre/corners first) dramatically improves pruning.

    This is the foundation of practical chess/checkers engines.
    """

    # Preferred move order: centre → corners → edges
    MOVE_ORDER = [4, 0, 2, 6, 8, 1, 3, 5, 7]

    def __init__(self, max_depth=4):
        self.max_depth = max_depth
        self.nodes_explored = 0
        self.nodes_pruned = 0

    def _ordered_moves(self, game):
        legal = set(game.legal_moves())
        return [m for m in self.MOVE_ORDER if m in legal]

    def h_alpha_beta(self, game, depth, alpha, beta, is_maximising):
        self.nodes_explored += 1

        if game.is_terminal() or depth == 0:
            return game.evaluate()

        if is_maximising:
            value = -math.inf
            for m in self._ordered_moves(game):
                game.make_move(m)
                value = max(value, self.h_alpha_beta(game, depth-1, alpha, beta, False))
                game.undo_move(m)
                alpha = max(alpha, value)
                if alpha >= beta:
                    self.nodes_pruned += 1
                    break
            return value
        else:
            value = math.inf
            for m in self._ordered_moves(game):
                game.make_move(m)
                value = min(value, self.h_alpha_beta(game, depth-1, alpha, beta, True))
                game.undo_move(m)
                beta = min(beta, value)
                if alpha >= beta:
                    self.nodes_pruned += 1
                    break
            return value

    def best_move(self, game):
        self.nodes_explored = 0
        self.nodes_pruned = 0
        is_max = (game.current_player == 1)
        best_val = -math.inf if is_max else math.inf
        best_m = None

        for m in self._ordered_moves(game):
            game.make_move(m)
            val = self.h_alpha_beta(game, self.max_depth-1, -math.inf, math.inf, not is_max)
            game.undo_move(m)

            if is_max and val > best_val:
                best_val, best_m = val, m
            elif not is_max and val < best_val:
                best_val, best_m = val, m

        return best_m, best_val


# ─────────────────────────────────────────────
# 4. MONTE-CARLO TREE SEARCH (MCTS)
# ─────────────────────────────────────────────

class MCTSNode:
    """
    A node in the MCTS search tree.

    Attributes:
        state       : cloned TicTacToe game at this node
        parent      : parent MCTSNode (None for root)
        move        : move that led from parent to this node
        children    : list of child MCTSNode
        wins        : cumulative wins from this node's perspective
        visits      : number of times node was visited
        untried     : moves not yet expanded
        player      : the player who *just moved* to reach this state
    """

    def __init__(self, state, parent=None, move=None):
        self.state = state.clone()
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0.0
        self.visits = 0
        # The player who will move FROM this node
        self.player = state.current_player
        self.untried = state.legal_moves()

    def ucb1(self, c=1.41):
        """Upper Confidence Bound for Trees (UCB1)."""
        if self.visits == 0:
            return math.inf
        exploitation = self.wins / self.visits
        exploration = c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

    def is_fully_expanded(self):
        return len(self.untried) == 0

    def best_child(self, c=1.41):
        return max(self.children, key=lambda n: n.ucb1(c))

    def expand(self):
        move = self.untried.pop(random.randrange(len(self.untried)))
        new_state = self.state.clone()
        new_state.make_move(move)
        child = MCTSNode(new_state, parent=self, move=move)
        self.children.append(child)
        return child

    def update(self, result):
        self.visits += 1
        # result is from the root player's perspective (+1/-1/0)
        self.wins += result


class MCTSAgent:
    """
    Monte-Carlo Tree Search.

    Four phases per iteration:
      1. Selection   – traverse tree using UCB1 until a non-fully-expanded node.
      2. Expansion   – add one new child for an untried move.
      3. Simulation  – play out a random game from the new child (rollout).
      4. Back-prop   – update win/visit counts up the tree.

    Parameters:
        iterations : number of MCTS iterations (simulations)
        c          : UCB1 exploration constant (√2 ≈ 1.41 is standard)
    """

    def __init__(self, iterations=1000, c=1.41):
        self.iterations = iterations
        self.c = c

    # ── Phase 1: Selection ────────────────────

    def _select(self, node):
        while not node.state.is_terminal():
            if not node.is_fully_expanded():
                return node
            node = node.best_child(self.c)
        return node

    # ── Phase 2: Expansion ────────────────────

    def _expand(self, node):
        if node.state.is_terminal():
            return node
        return node.expand()

    # ── Phase 3: Simulation (rollout) ─────────

    def _simulate(self, node):
        sim = node.state.clone()
        while not sim.is_terminal():
            sim.make_move(random.choice(sim.legal_moves()))
        return sim.result()   # +1 X wins, -1 O wins, 0 draw

    # ── Phase 4: Back-propagation ─────────────

    def _backpropagate(self, node, result, root_player):
        while node is not None:
            node.visits += 1
            # Wins are from root_player's perspective
            if result == root_player:
                node.wins += 1
            elif result == 0:
                node.wins += 0.5
            node = node.parent

    # ── Main search ───────────────────────────

    def best_move(self, game):
        root = MCTSNode(game)
        root_player = game.current_player

        for _ in range(self.iterations):
            leaf = self._select(root)
            child = self._expand(leaf)
            result = self._simulate(child)
            self._backpropagate(child, result, root_player)

        # Choose the most-visited child (robust child criterion)
        if not root.children:
            return game.legal_moves()[0], 0
        best = max(root.children, key=lambda n: n.visits)
        win_rate = best.wins / best.visits if best.visits else 0
        return best.move, win_rate
