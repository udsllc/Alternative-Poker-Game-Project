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

## Sample Session

```
====================================================
              DRAFT  POKER
  Draft your deck. Read your opponent. Win.
====================================================

  How many rounds?
    (4)  Quick match
    (8)  Standard match
    (12) Long match
  > 4

  How do you want to build your deck?
    (d) Draft  — pick your cards one by one
    (r) Random — get a random 20-card deck
  > r

=== Random Deck Mode ===
Your deck:     2♣  5♣  7♣  9♣  J♣  3♦  6♦  8♦  Q♦  A♦  4♥  7♥  10♥  K♥  2♠  5♠  8♠  J♠  Q♠  A♠
Opponent deck: 2♦  4♦  7♦  9♦  K♦  3♥  6♥  8♥  J♥  A♥  2♣  5♣  9♣  Q♣  A♣  3♠  6♠  10♠  K♠  4♥

Press Enter to begin the match...

────────────────────────────────────────────────────
  Round 1 of 4    |    Score: You 0 – 0 Opponent
────────────────────────────────────────────────────
  Your hand: 9♣  J♣  Q♦  4♥  A♠   →   High Card

  Discard phase — your hand:
    1. 9♣
    2. J♣
    3. Q♦
    4. 4♥
    5. A♠
  Current hand: High Card
  Enter card numbers to discard (e.g. '1 3'), or press Enter to keep all.
  You may discard up to 3 cards.  (q) Quit
  > 1 3 4
  You drew 3 card(s).
  New hand : J♣  A♠  8♦  J♠  Q♠   →   One Pair
  Opponent draws 2 card(s).

  Your action:
    (f) Fold
    (c) Check
    (r) Raise
    (v) View remaining deck
    (q) Quit game
  > v

  Remaining deck (12 cards):
    ♣ Clubs: 5♣  7♣
    ♦ Diamonds: 3♦  6♦
    ♥ Hearts: 7♥  10♥  K♥
    ♠ Spades: 2♠  5♠  A♠

  Your action:
    (f) Fold
    (c) Check
    (r) Raise
    (v) View remaining deck
    (q) Quit game
  > r

  Raise amount:
    (s) Small  — 2 points
    (m) Medium — 3 points
    (a) All-in — 5 points
    (q) Quit game
  > s

  Opponent calls.

  Your hand: J♣  J♠  Q♠  8♦  A♠   →   One Pair
  Opponent : 6♥  6♦  K♦  9♦  A♥   →   One Pair

  >>> You win this round! (+2 points) <<<

  Press Enter for the next round... (q to quit)

────────────────────────────────────────────────────
  Round 2 of 4    |    Score: You 2 – 0 Opponent
────────────────────────────────────────────────────
  Your hand: 5♣  7♥  10♥  K♥  2♠   →   High Card

  Discard phase — your hand:
    1. 5♣
    2. 7♥
    3. 10♥
    4. K♥
    5. 2♠
  Current hand: High Card
  Enter card numbers to discard (e.g. '1 3'), or press Enter to keep all.
  You may discard up to 3 cards.  (q) Quit
  > 1 2 5
  You drew 3 card(s).
  New hand : 10♥  K♥  3♦  6♦  7♣   →   High Card
  Opponent stands pat.

  Your action:
    (f) Fold
    (c) Check
    (r) Raise
    (v) View remaining deck
    (q) Quit game
  > c

  Opponent raises! (3 points at stake) Do you:
  Call or fold?
    (c) Call
    (f) Fold
    (q) Quit game
  > f

  You fold.
  Opponent had: 3♠  3♥  8♥  J♥  A♥   →   One Pair
  Opponent wins 3 points.

  Press Enter for the next round... (q to quit)

────────────────────────────────────────────────────
  Round 3 of 4    |    Score: You 2 – 3 Opponent
────────────────────────────────────────────────────
  Your hand: A♦  Q♠  J♣  8♦  5♣   →   High Card

  Discard phase — your hand:
    1. A♦
    2. Q♠
    3. J♣
    4. 8♦
    5. 5♣
  Current hand: High Card
  Enter card numbers to discard (e.g. '1 3'), or press Enter to keep all.
  You may discard up to 3 cards.  (q) Quit
  > 3 4 5
  You drew 3 card(s).
  New hand : A♦  Q♠  K♥  Q♦  7♣   →   One Pair
  Opponent draws 3 card(s).

  Your action:
    (f) Fold
    (c) Check
    (r) Raise
    (v) View remaining deck
    (q) Quit game
  > r

  Raise amount:
    (s) Small  — 2 points
    (m) Medium — 3 points
    (a) All-in — 5 points
    (q) Quit game
  > m

  Opponent folds. You win 3 points!

  Press Enter for the next round... (q to quit)

────────────────────────────────────────────────────
  Round 4 of 4    |    Score: You 5 – 3 Opponent
────────────────────────────────────────────────────
  Your hand: 7♣  6♦  K♥  2♠  A♦   →   High Card

  Discard phase — your hand:
    1. 7♣
    2. 6♦
    3. K♥
    4. 2♠
    5. A♦
  Current hand: High Card
  Enter card numbers to discard (e.g. '1 3'), or press Enter to keep all.
  You may discard up to 3 cards.  (q) Quit
  > 1 2 4
  You drew 3 card(s).
  New hand : K♥  A♦  K♣  5♠  J♦   →   One Pair
  Opponent draws 1 card(s).

  Your action:
    (f) Fold
    (c) Check
    (r) Raise
    (v) View remaining deck
    (q) Quit game
  > r

  Raise amount:
    (s) Small  — 2 points
    (m) Medium — 3 points
    (a) All-in — 5 points
    (q) Quit game
  > a

  Opponent calls.

  Your hand: K♥  K♣  A♦  J♦  5♠   →   One Pair
  Opponent : 10♠  10♦  A♣  8♠  2♦   →   One Pair

  >>> You win this round! (+5 points) <<<

====================================================
  FINAL SCORE:  You 10 – 3 Opponent
====================================================
  You win the match! Well played.

  Opponent's final read on you:
  Rounds tracked : 4
  Fold rate      : 25%  (1 folds)
  Aggression     : 75%  (3 raises)
  Bluff rate     : 0%  (0 caught)
  Read: raises frequently — calling down lighter.
====================================================
```

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
