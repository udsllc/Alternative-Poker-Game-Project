# Draft Poker

A strategic card game built in Python that combines poker-style hand rankings with deck drafting and an adaptive bluffing opponent.

## Concept

Standard poker is mostly chance. Draft Poker changes that by letting you shape the deck before a single card is dealt — making hand probabilities partially knowable and turning the pre-game draft into a genuine strategic layer.

### Key Twists

**Deck Drafting**  
Before each match, you and the computer take turns picking cards from a shared 52-card pool in a snake draft (coin flip determines who goes first). Each player ends up with a 20-card personal deck.

**Two Deck Modes**  
- **Draft** — pick your 20 cards one by one, alternating with the opponent
- **Random** — skip the draft and get a shuffled random deck

**Intelligent Opponent**  
The opponent is not random. It tracks your behavior across every round — how often you fold, how aggressively you bet, whether you bluff with weak hands — and uses those tendencies to decide whether to value-bet, bluff, or call you down.

## Gameplay

1. Choose match length: 4 (quick), 8 (standard), or 12 (long) rounds
2. Choose draft or random deck mode
3. (If drafting) Alternate picks from the shared pool until each side has 20 cards
4. Each round deals 5 cards from your deck — choose to **fold**, **check**, or **raise**; the opponent responds based on its model of you
5. Points are awarded per round (fold = opponent wins that round; showdown = best hand wins)
6. After all rounds the match score is displayed along with the opponent's final read on your tendencies

### Betting Flow

```
Player:    fold  →  opponent wins round
Player:    check →  opponent may check (showdown) or raise (you call/fold)
Player:    raise →  opponent may fold (you win) or call (showdown)
```

### Hand Rankings (low → high)

High Card · One Pair · Two Pair · Three of a Kind · Straight · Flush · Full House · Four of a Kind · Straight Flush · Royal Flush

## Technical Design

| Concept | Implementation |
|---|---|
| Card representation | `namedtuple('Card', ['rank', 'suit'])` |
| Card pool during drafting | Dictionary mapping `Card → availability (0/1)` |
| Player/opponent decks and hands | Lists (deck mutated in-place as cards are dealt) |
| Card uniqueness in draft | Dictionary key lookup (no duplicates possible) |
| Hand evaluation | Tuple comparison `(rank_index, [tiebreak_vals])` |
| Opponent behavior tracking | Dictionary of running counters (folds, raises, bluffs caught) |
| Opponent decision logic | Derived rates (fold rate, aggression rate, bluff rate) scaled against hand strength |

## Project Structure

```
CS1_FP/
├── main.py       # Entry point, game loop, round logic, betting flow
├── deck.py       # Card definitions, pool building, draft, random mode, dealing
├── hand.py       # Hand evaluation, ranking, comparison, display
├── opponent.py   # Adaptive opponent agent (tracks tendencies, decides actions)
└── README.md
```

## Running the Game

```bash
python main.py
```

Requires Python 3.10+. No external dependencies.

## AI Usage Statement

The core design of this project — the game concept, the data structures, the draft mechanic, the opponent's tendency-tracking logic, and the overall program architecture — was my own work. I used AI assistance in the following supporting ways:

- **Formatting and style** — cleaning up print layout (the dividers, spacing, and score display) so the terminal output was readable
- **Docstrings and comments** — help wording inline documentation and function docstrings clearly
- **Debugging** — talking through off-by-one issues in the snake draft loop and a bug in the ace-low straight detection
- **Syntax lookups** — quick questions about Python syntax (e.g., `namedtuple`, `Counter`, `random.choices` with weights)
- **README writing** — drafting and organizing this document based on the completed code

All logic decisions — how the opponent models the player, how hand strength maps to betting thresholds, how the draft alternation works — were designed and implemented by me.

## Course

CS1 Final Project
