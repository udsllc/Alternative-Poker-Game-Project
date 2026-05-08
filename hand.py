from collections import Counter
from deck import card_str, RANK_VALUE, SUIT_SYMBOLS

HAND_NAMES = [
    'High Card',
    'One Pair',
    'Two Pair',
    'Three of a Kind',
    'Straight',
    'Flush',
    'Full House',
    'Four of a Kind',
    'Straight Flush',
    'Royal Flush',
]


def _rank_vals(hand):
    return sorted([RANK_VALUE[c.rank] for c in hand], reverse=True)


def _is_flush(hand):
    return len({c.suit for c in hand}) == 1


def _is_straight(hand):
    vals = sorted({RANK_VALUE[c.rank] for c in hand})
    if len(vals) != 5:
        return False, 0
    if vals[-1] - vals[0] == 4:
        return True, vals[-1]
    if vals == [2, 3, 4, 5, 14]:   # Ace-low straight (A-2-3-4-5)
        return True, 5
    return False, 0


def evaluate_hand(hand):
    """
    Returns a comparable tuple (rank_index, [tiebreak_values]).
    Higher tuple = stronger hand. Tiebreak list breaks ties within the same rank.

    Hand rank index:
      0 High Card | 1 One Pair | 2 Two Pair | 3 Three of a Kind
      4 Straight  | 5 Flush    | 6 Full House | 7 Four of a Kind
      8 Straight Flush | 9 Royal Flush
    """
    values = _rank_vals(hand)
    flush = _is_flush(hand)
    straight, straight_high = _is_straight(hand)

    # counts: {rank_value: frequency}, sorted by (frequency desc, rank desc)
    counts = Counter(RANK_VALUE[c.rank] for c in hand)
    groups = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    group_counts = [g[1] for g in groups]
    group_vals  = [g[0] for g in groups]

    if flush and straight:
        if straight_high == 14:
            return (9, [14])                # Royal Flush
        return (8, [straight_high])         # Straight Flush

    if group_counts[0] == 4:
        return (7, group_vals)              # Four of a Kind: [quads, kicker]

    if group_counts[:2] == [3, 2]:
        return (6, group_vals)              # Full House: [trips, pair]

    if flush:
        return (5, values)                  # Flush: all five cards

    if straight:
        return (4, [straight_high])         # Straight

    if group_counts[0] == 3:
        return (3, group_vals)              # Three of a Kind: [trips, k1, k2]

    if group_counts[:2] == [2, 2]:
        return (2, group_vals)              # Two Pair: [high, low, kicker]

    if group_counts[0] == 2:
        return (1, group_vals)              # One Pair: [pair, k1, k2, k3]

    return (0, values)                      # High Card


def hand_rank_name(hand):
    rank_index, _ = evaluate_hand(hand)
    return HAND_NAMES[rank_index]


def compare_hands(hand_a, hand_b):
    """Returns 1 if hand_a wins, -1 if hand_b wins, 0 for a tie."""
    eval_a = evaluate_hand(hand_a)
    eval_b = evaluate_hand(hand_b)
    if eval_a > eval_b:
        return 1
    elif eval_a < eval_b:
        return -1
    return 0


def display_hand(hand, label="Hand"):
    cards = '  '.join(card_str(c) for c in hand)
    name = hand_rank_name(hand)
    print(f"  {label}: {cards}   →   {name}")
