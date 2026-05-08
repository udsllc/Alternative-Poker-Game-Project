from collections import Counter
from hand import evaluate_hand
from deck import RANK_VALUE

# Hand strength index runs 0–9 (High Card → Royal Flush).
# Dividing by 9 gives a 0.0–1.0 scale used throughout this module.
_MAX_RANK = 9


class Opponent:
    def __init__(self):
        # Every player tendency is stored in this dictionary.
        # Values accumulate across rounds and drive the agent's decisions.
        self.player_stats = {
            'rounds_played': 0,
            'folds':         0,   # player folded before showdown
            'checks':        0,   # player checked or called without raising
            'raises':        0,   # player raised/bet aggressively
            'bluffs_caught': 0,   # player raised but showed a weak hand at showdown
        }

    # ------------------------------------------------------------------
    # Recording player behavior
    # ------------------------------------------------------------------

    def record_player_action(self, action):
        """Call once per round with the player's primary action: 'fold', 'check', or 'raise'."""
        self.player_stats['rounds_played'] += 1
        if action == 'fold':
            self.player_stats['folds'] += 1
        elif action == 'raise':
            self.player_stats['raises'] += 1
        else:
            self.player_stats['checks'] += 1

    def record_showdown(self, player_hand, player_action):
        """
        After a showdown, check whether the player bluffed.
        A 'raise' followed by a high card or one pair counts as a caught bluff.
        """
        if player_action == 'raise':
            hand_rank = evaluate_hand(player_hand)[0]
            if hand_rank <= 1:   # High Card or One Pair
                self.player_stats['bluffs_caught'] += 1

    # ------------------------------------------------------------------
    # Derived tendency rates
    # ------------------------------------------------------------------

    def _fold_rate(self):
        played = self.player_stats['rounds_played']
        return self.player_stats['folds'] / played if played > 0 else 0.30

    def _aggression_rate(self):
        played = self.player_stats['rounds_played']
        return self.player_stats['raises'] / played if played > 0 else 0.30

    def _bluff_rate(self):
        raises = self.player_stats['raises']
        return self.player_stats['bluffs_caught'] / raises if raises > 0 else 0.20

    # ------------------------------------------------------------------
    # Decision logic
    # ------------------------------------------------------------------

    def decide_action(self, hand, player_action):
        """
        Choose an action given the opponent's current hand and what the player just did.

        Returns one of: 'fold', 'call', 'raise'
        ('raise' may be a value bet or a bluff depending on hand strength)
        """
        strength = evaluate_hand(hand)[0] / _MAX_RANK   # 0.0 – 1.0

        fold_rate    = self._fold_rate()
        aggression   = self._aggression_rate()
        bluff_rate   = self._bluff_rate()

        # ---- Player raised -----------------------------------------------
        if player_action == 'raise':
            # Does the player raise a lot (likely bluffing) or rarely (likely strong)?
            if aggression > 0.50 or bluff_rate > 0.40:
                # Treat the raise as a potential bluff — call with decent hands
                call_threshold = 0.22   # Two Pair or better
            else:
                # Respect the raise — need something solid to continue
                call_threshold = 0.44   # Straight or better

            if strength >= call_threshold:
                return 'call'
            return 'fold'

        # ---- Player checked or called ------------------------------------
        # Decide whether to bluff, value-bet, or check behind.

        # Bluff: player folds a lot AND our hand is weak
        if fold_rate > 0.45 and strength < 0.33:
            return 'raise'

        # Value bet: hand is strong enough to expect to get paid
        if strength >= 0.44:    # Straight or better
            return 'raise'

        # Not strong enough to bet, not a good bluff spot — check behind
        return 'call'

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def decide_raise_amount(self, hand):
        """Return point value the opponent bets: 2 (small), 3 (medium), or 5 (all-in)."""
        strength = evaluate_hand(hand)[0] / _MAX_RANK
        bluff_rate = self._bluff_rate()
        if strength >= 0.67:        # Full house or better — go big
            return 5
        if strength >= 0.33:        # Two pair to flush — medium value bet
            return 3
        if bluff_rate < 0.25:       # Hasn't been caught bluffing much — small bluff
            return 2
        return 2                    # Weak hand, small bluff either way

    def choose_discards(self, hand):
        """Return a list of indices (0-based) to discard, up to 3."""
        rank_counts = Counter(RANK_VALUE[c.rank] for c in hand)
        suit_counts = Counter(c.suit for c in hand)

        # Keep any rank that appears in a pair, trips, or quads
        kept_ranks = {r for r, n in rank_counts.items() if n >= 2}

        # If 4 cards share a suit, chase the flush
        flush_suit = next((s for s, n in suit_counts.items() if n >= 4), None)
        if flush_suit:
            discard_indices = [i for i, c in enumerate(hand) if c.suit != flush_suit]
        elif kept_ranks:
            discard_indices = [i for i, c in enumerate(hand)
                               if RANK_VALUE[c.rank] not in kept_ranks]
        else:
            # No made hand — keep top 2 by rank, discard the rest
            by_rank = sorted(range(5), key=lambda i: RANK_VALUE[hand[i].rank], reverse=True)
            keep = set(by_rank[:2])
            discard_indices = [i for i in range(5) if i not in keep]

        return discard_indices[:3]

    def print_tendencies(self):
        """Print the opponent's current read on the player."""
        played = self.player_stats['rounds_played']
        if played == 0:
            print("  No data yet — playing blind.")
            return

        print(f"  Rounds tracked : {played}")
        print(f"  Fold rate      : {self._fold_rate():.0%}  ({self.player_stats['folds']} folds)")
        print(f"  Aggression     : {self._aggression_rate():.0%}  ({self.player_stats['raises']} raises)")
        print(f"  Bluff rate     : {self._bluff_rate():.0%}  ({self.player_stats['bluffs_caught']} caught)")

        fold_rate  = self._fold_rate()
        aggression = self._aggression_rate()
        if fold_rate > 0.45:
            print("  Read: folds too much — bluffing more aggressively.")
        elif aggression > 0.50:
            print("  Read: raises frequently — calling down lighter.")
        else:
            print("  Read: balanced player — playing straightforward.")
