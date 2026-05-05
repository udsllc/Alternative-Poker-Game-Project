# Draft Poker

A strategic card game built in Python that combines poker-style hand rankings with deck drafting and an intelligent bluffing opponent.

## Concept

Standard poker is mostly chance. Draft Poker changes that by letting you shape the deck before a single card is dealt — making hand probabilities partially knowable and turning the pre-game draft into a genuine strategic layer.

### Key Twists

**Deck Drafting**
Before each match, you and the computer opponent take turns picking cards from a shared pool to build personal 20-card decks. The cards you draft (and the ones you leave behind) shift the probability landscape for the entire game.

**Intelligent Opponent**
The computer opponent is not random. It tracks your behavior across rounds — how often you fold, how aggressively you bet, whether you bluff — and uses that model to decide dynamically whether to bluff, call, or raise against you.

## Gameplay

- Both players draft a 20-card deck from a shared pool before the match begins
- Rounds follow standard poker hand rankings (pair, two pair, straight, flush, etc.)
- The opponent adapts its strategy based on a running model of your tendencies
- Winning rounds scores points; match ends after a set number of rounds

## Technical Design

| Concept | Implementation |
|---|---|
| Card pool during drafting | Dictionary (card → available count) |
| Player/opponent hands and decks | Lists |
| Card uniqueness enforcement | Sets |
| Opponent behavior tracking | Dictionary (tendency → frequency/value) |

## Project Structure

```
CS1_FP/
├── main.py          # Entry point, game loop
├── deck.py          # Card definitions, deck building, drafting logic
├── hand.py          # Hand evaluation and poker ranking
├── opponent.py      # Intelligent opponent agent
└── README.md
```

## Running the Game

```bash
python main.py
```

Requires Python 3.10+. No external dependencies.

## Course

CS1 Final Project
