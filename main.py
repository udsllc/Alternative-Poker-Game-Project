from deck import build_card_pool, run_draft, random_decks, deal_hand, discard_and_draw, card_str, SUITS, SUIT_SYMBOLS, RANK_VALUE
from hand import compare_hands, display_hand, hand_rank_name
from opponent import Opponent


class QuitGame(Exception):
    pass


def _check_quit(raw):
    if raw.strip().lower() in ('q', 'quit', 'exit'):
        raise QuitGame()


# -----------------------------------------------------------------------
# Input helpers
# -----------------------------------------------------------------------

def _prompt_discards(hand):
    """Show the hand numbered 1-5 and return a list of 0-based indices to discard (0-3 cards)."""
    print("\n  Discard phase — your hand:")
    for i, card in enumerate(hand, 1):
        print(f"    {i}. {card_str(card)}")
    print(f"  Current hand: {hand_rank_name(hand)}")
    print("  Enter card numbers to discard (e.g. '1 3'), or press Enter to keep all.")
    print("  You may discard up to 3 cards.  (q) Quit")
    while True:
        raw = input("  > ").strip()
        _check_quit(raw)
        if raw == '':
            return []
        parts = raw.split()
        if all(p.isdigit() for p in parts):
            indices = [int(p) - 1 for p in parts]
            if (len(indices) <= 3
                    and all(0 <= idx < 5 for idx in indices)
                    and len(set(indices)) == len(indices)):
                return indices
        print("  Enter up to 3 numbers from 1–5, separated by spaces, or press Enter to keep all.")


def _show_remaining_deck(deck):
    """Print the player's remaining deck grouped by suit."""
    print(f"\n  Remaining deck ({len(deck)} cards):")
    for suit in SUITS:
        suited = sorted([c for c in deck if c.suit == suit],
                        key=lambda c: RANK_VALUE[c.rank])
        if suited:
            print(f"    {SUIT_SYMBOLS[suit]} {suit}: {'  '.join(card_str(c) for c in suited)}")


def _prompt_action(player_deck):
    """Ask the player fold / check / raise. Returns 'fold', 'check', or 'raise'."""
    print("\n  Your action:")
    print("    (f) Fold")
    print("    (c) Check")
    print("    (r) Raise")
    print("    (v) View remaining deck")
    print("    (q) Quit game")
    while True:
        choice = input("  > ").strip().lower()
        _check_quit(choice)
        if choice in ('f', 'fold'):
            return 'fold'
        if choice in ('c', 'check', 'call'):
            return 'check'
        if choice in ('r', 'raise'):
            return 'raise'
        if choice in ('v', 'view'):
            _show_remaining_deck(player_deck)
            continue
        print("  Please enter f, c, r, v, or q.")


def _prompt_call_or_fold():
    """After opponent raises, ask player to call or fold."""
    print("  Call or fold?")
    print("    (c) Call")
    print("    (f) Fold")
    print("    (q) Quit game")
    while True:
        choice = input("  > ").strip().lower()
        _check_quit(choice)
        if choice in ('c', 'call'):
            return 'call'
        if choice in ('f', 'fold'):
            return 'fold'
        print("  Please enter c, f, or q.")


def _prompt_raise_amount():
    """Ask how much to raise. Returns the point value at stake."""
    print("\n  Raise amount:")
    print("    (s) Small  — 2 points")
    print("    (m) Medium — 3 points")
    print("    (a) All-in — 5 points")
    print("    (q) Quit game")
    while True:
        choice = input("  > ").strip().lower()
        _check_quit(choice)
        if choice in ('s', 'small'):
            return 2
        if choice in ('m', 'medium'):
            return 3
        if choice in ('a', 'all-in', 'allin', 'all'):
            return 5
        print("  Please enter s, m, a, or q.")


# -----------------------------------------------------------------------
# Round logic
# -----------------------------------------------------------------------

def _showdown(player_hand, opp_hand, score, points=1):
    """Reveal both hands and award points."""
    print()
    display_hand(player_hand, "Your hand")
    display_hand(opp_hand,    "Opponent ")
    print()

    pts_label = f"{points} point{'s' if points != 1 else ''}"
    result = compare_hands(player_hand, opp_hand)
    if result == 1:
        print(f"  >>> You win this round! (+{pts_label}) <<<")
        score['player'] += points
    elif result == -1:
        print(f"  >>> Opponent wins this round. (+{pts_label}) <<<")
        score['opponent'] += points
    else:
        print("  >>> Tie — no points awarded. <<<")
    return result


def play_round(round_num, rounds, player_deck, opp_deck, opp, score):
    divider = '─' * 52
    print(f"\n{divider}")
    print(f"  Round {round_num} of {rounds}    |    "
          f"Score: You {score['player']} – {score['opponent']} Opponent")
    print(divider)

    player_hand = deal_hand(player_deck)
    opp_hand    = deal_hand(opp_deck)

    # --- Discard phase -------------------------------------------------------
    display_hand(player_hand, "Your hand")
    discard_indices = _prompt_discards(player_hand)
    if discard_indices:
        player_hand = discard_and_draw(player_deck, player_hand, discard_indices)
        print(f"  You drew {len(discard_indices)} card(s).")
        display_hand(player_hand, "New hand ")

    opp_discards = opp.choose_discards(opp_hand)
    opp_hand = discard_and_draw(opp_deck, opp_hand, opp_discards)
    if opp_discards:
        print(f"  Opponent draws {len(opp_discards)} card(s).")
    else:
        print("  Opponent stands pat.")

    # --- Betting phase -------------------------------------------------------
    # Hands are always recycled back into the decks after the round.
    try:
        player_action = _prompt_action(player_deck)

        # ---- Player folds immediately ------------------------------------
        if player_action == 'fold':
            print("\n  You folded.")
            display_hand(opp_hand, "Opponent had")
            opp.record_player_action('fold')
            score['opponent'] += 1
            print("  Opponent wins 1 point.")
            return

        # ---- Player raises -----------------------------------------------
        if player_action == 'raise':
            points = _prompt_raise_amount()
            opp_action = opp.decide_action(opp_hand, 'raise')
            if opp_action == 'fold':
                pts_label = f"{points} point{'s' if points != 1 else ''}"
                print(f"\n  Opponent folds. You win {pts_label}!")
                score['player'] += points
                opp.record_player_action('raise')
                return
            print("\n  Opponent calls.")
            _showdown(player_hand, opp_hand, score, points)
            opp.record_player_action('raise')
            opp.record_showdown(player_hand, 'raise')
            return

        # ---- Player checks — opponent responds ---------------------------
        opp_action = opp.decide_action(opp_hand, 'check')

        if opp_action == 'raise':
            opp_points = opp.decide_raise_amount(opp_hand)
            pts_label = f"{opp_points} point{'s' if opp_points != 1 else ''}"
            print(f"\n  Opponent raises! ({pts_label} at stake) Do you:")
            response = _prompt_call_or_fold()
            if response == 'fold':
                print("\n  You fold.")
                display_hand(opp_hand, "Opponent had")
                opp.record_player_action('fold')
                score['opponent'] += opp_points
                print(f"  Opponent wins {pts_label}.")
                return
            print("\n  You call.")
            _showdown(player_hand, opp_hand, score, opp_points)
            opp.record_player_action('check')
            opp.record_showdown(player_hand, 'check')
            return

        # Both checked — go to showdown for 1 point
        print("\n  Opponent checks.")
        _showdown(player_hand, opp_hand, score)
        opp.record_player_action('check')
        opp.record_showdown(player_hand, 'check')

    finally:
        # Return hands to decks so longer matches don't exhaust the 20-card pool.
        player_deck.extend(player_hand)
        opp_deck.extend(opp_hand)


# -----------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------

def main():
    print("=" * 52)
    print("              DRAFT  POKER")
    print("  Draft your deck. Read your opponent. Win.")
    print("=" * 52)

    print("\n  How many rounds?")
    print("    (4)  Quick match")
    print("    (8)  Standard match")
    print("    (12) Long match")
    while True:
        rc = input("  > ").strip()
        if rc in ('4', '8', '12'):
            rounds = int(rc)
            break
        print("  Please enter 4, 8, or 12.")

    print("\n  How do you want to build your deck?")
    print("    (d) Draft  — pick your cards one by one")
    print("    (r) Random — get a random 20-card deck")
    while True:
        mode = input("  > ").strip().lower()
        if mode in ('d', 'draft'):
            pool = build_card_pool()
            player_deck, opp_deck = run_draft(pool)
            break
        if mode in ('r', 'random'):
            pool = build_card_pool()
            player_deck, opp_deck = random_decks(pool)
            break
        print("  Please enter d or r.")

    input("\nPress Enter to begin the match...")

    opp   = Opponent()
    score = {'player': 0, 'opponent': 0}

    try:
        for round_num in range(1, rounds + 1):
            play_round(round_num, rounds, player_deck, opp_deck, opp, score)
            if round_num < rounds:
                raw = input("\n  Press Enter for the next round... (q to quit)  ")
                _check_quit(raw)
    except QuitGame:
        print("\n  Quitting game...")

    # Final result
    print(f"\n{'=' * 52}")
    print(f"  FINAL SCORE:  You {score['player']} – {score['opponent']} Opponent")
    print('=' * 52)
    if score['player'] > score['opponent']:
        print("  You win the match! Well played.")
    elif score['opponent'] > score['player']:
        print("  Opponent wins. Better luck next time.")
    else:
        print("  It's a draw!")

    print("\n  Opponent's final read on you:")
    opp.print_tendencies()
    print("=" * 52)


if __name__ == '__main__':
    main()
