import random
from collections import namedtuple

Card = namedtuple('Card', ['rank', 'suit'])

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
SUIT_SYMBOLS = {'Clubs': '♣', 'Diamonds': '♦', 'Hearts': '♥', 'Spades': '♠'}

RANK_VALUE = {rank: i + 2 for i, rank in enumerate(RANKS)}  # '2'->2 ... 'A'->14


def card_str(card):
    return f"{card.rank}{SUIT_SYMBOLS[card.suit]}"


def build_card_pool():
    """Returns a dict mapping every Card in a standard 52-card deck to its availability (1 = available, 0 = drafted)."""
    return {Card(rank, suit): 1 for rank in RANKS for suit in SUITS}


def display_pool(pool):
    """Print available cards grouped by suit, numbered for selection."""
    available = [card for card, count in pool.items() if count > 0]
    print("\n--- Available Cards ---")
    for suit in SUITS:
        suited = [c for c in available if c.suit == suit]
        if suited:
            cards_str = '  '.join(f"{card_str(c)}" for c in suited)
            print(f"  {SUIT_SYMBOLS[suit]} {suit}: {cards_str}")
    print(f"  ({len(available)} cards remaining)\n")


def _numbered_available(pool):
    """Return a list of available cards in a stable display order."""
    return [
        card for suit in SUITS for rank in RANKS
        for card in [Card(rank, suit)]
        if pool.get(card, 0) == 1
    ]


def _player_pick(pool):
    """Show available cards and prompt the player to pick one by number."""
    available = _numbered_available(pool)
    print("Available cards (enter the number to pick):")
    for i, card in enumerate(available, 1):
        end = '\n' if i % 13 == 0 else '  '
        print(f"  {i:>2}. {card_str(card)}", end=end)
    print()

    while True:
        raw = input("Your pick: ").strip()
        if raw.isdigit():
            choice = int(raw)
            if 1 <= choice <= len(available):
                picked = available[choice - 1]
                pool[picked] = 0
                return picked
        print(f"  Please enter a number between 1 and {len(available)}.")


def _opponent_draft_pick(pool):
    """Computer picks during drafting — weights toward high-rank cards."""
    available = [card for card, count in pool.items() if count > 0]
    weights = [RANK_VALUE[card.rank] for card in available]
    picked = random.choices(available, weights=weights, k=1)[0]
    pool[picked] = 0
    return picked


def run_draft(pool):
    """
    Alternating snake draft: player and opponent each pick 20 cards.
    Returns (player_deck, opponent_deck) as lists of Card.
    """
    player_deck = []
    opponent_deck = []

    # Coin flip determines who picks first
    player_goes_first = random.choice([True, False])
    first = "You" if player_goes_first else "Opponent"
    print(f"\n=== Draft Phase ===")
    print(f"Coin flip: {first} pick first.\n")

    for pick_num in range(40):  # 20 picks each side
        # True snake draft: pairs of picks reverse each round (1-2-2-1-1-2-2-1...)
        pair_num = pick_num // 2
        within_pair = pick_num % 2
        is_first_turn = (pair_num % 2 == 0) == (within_pair == 0)
        is_player_turn = is_first_turn if player_goes_first else not is_first_turn

        if is_player_turn:
            picks_so_far = len(player_deck)
            print(f"--- Your pick {picks_so_far + 1}/20 ---")
            display_pool(pool)
            card = _player_pick(pool)
            player_deck.append(card)
            print(f"  You picked: {card_str(card)}\n")
        else:
            card = _opponent_draft_pick(pool)
            opponent_deck.append(card)
            print(f"  Opponent picked: {card_str(card)}")

    print("\n=== Draft Complete ===")
    print(f"Your deck:     {', '.join(card_str(c) for c in sorted(player_deck, key=lambda c: (c.suit, RANK_VALUE[c.rank])))}")
    print(f"Opponent deck: {', '.join(card_str(c) for c in sorted(opponent_deck, key=lambda c: (c.suit, RANK_VALUE[c.rank])))}")

    return player_deck, opponent_deck


def random_decks(pool):
    """Randomly assign 20 cards to each player without drafting."""
    all_cards = [card for card, count in pool.items() if count > 0]
    random.shuffle(all_cards)
    player_deck   = all_cards[:20]
    opponent_deck = all_cards[20:40]

    print("\n=== Random Deck Mode ===")
    print(f"Your deck:     {', '.join(card_str(c) for c in sorted(player_deck,   key=lambda c: (c.suit, RANK_VALUE[c.rank])))}")
    print(f"Opponent deck: {', '.join(card_str(c) for c in sorted(opponent_deck, key=lambda c: (c.suit, RANK_VALUE[c.rank])))}")

    return player_deck, opponent_deck


def deal_hand(deck, hand_size=5):
    """
    Deal hand_size cards from the deck (modifies deck in place).
    Returns the dealt hand as a list.
    """
    hand = random.sample(deck, hand_size)
    for card in hand:
        deck.remove(card)
    return hand


def discard_and_draw(deck, hand, discard_indices):
    """
    Remove cards at discard_indices from hand, shuffle them back into the deck,
    and draw replacements. Returns the new hand as a list.
    """
    if not discard_indices:
        return hand
    discards = [hand[i] for i in discard_indices]
    kept     = [c for i, c in enumerate(hand) if i not in discard_indices]
    deck.extend(discards)
    random.shuffle(deck)
    drawn = [deck.pop() for _ in discards]
    return kept + drawn
