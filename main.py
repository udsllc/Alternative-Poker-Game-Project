from deck import build_card_pool, run_draft, random_decks, deal_hand
from hand import compare_hands, display_hand
from opponent import Opponent

ROUNDS = 4   # 20-card decks / 5-card hands = exactly 4 rounds


# -----------------------------------------------------------------------
# Input helpers
# -----------------------------------------------------------------------

def _prompt_action():
    """Ask the player fold / check / raise. Returns 'fold', 'check', or 'raise'."""
    print("\n  Your action:")
    print("    (f) Fold")
    print("    (c) Check")
    print("    (r) Raise")
    while True:
        choice = input("  > ").strip().lower()
        if choice in ('f', 'fold'):
            return 'fold'
        if choice in ('c', 'check', 'call'):
            return 'check'
        if choice in ('r', 'raise'):
            return 'raise'
        print("  Please enter f, c, or r.")


def _prompt_call_or_fold():
    """After opponent raises, ask player to call or fold."""
    print("\n  Opponent raises! Do you:")
    print("    (c) Call")
    print("    (f) Fold")
    while True:
        choice = input("  > ").strip().lower()
        if choice in ('c', 'call'):
            return 'call'
        if choice in ('f', 'fold'):
            return 'fold'
        print("  Please enter c or f.")


# -----------------------------------------------------------------------
# Round logic
# -----------------------------------------------------------------------

def _showdown(player_hand, opp_hand, score):
    """Reveal both hands and award the point."""
    print()
    display_hand(player_hand, "Your hand")
    display_hand(opp_hand,    "Opponent ")
    print()

    result = compare_hands(player_hand, opp_hand)
    if result == 1:
        print("  >>> You win this round! <<<")
        score['player'] += 1
    elif result == -1:
        print("  >>> Opponent wins this round. <<<")
        score['opponent'] += 1
    else:
        print("  >>> Tie — no point awarded. <<<")
    return result


def play_round(round_num, player_deck, opp_deck, opp, score):
    divider = '─' * 52
    print(f"\n{divider}")
    print(f"  Round {round_num} of {ROUNDS}    |    "
          f"Score: You {score['player']} – {score['opponent']} Opponent")
    print(divider)

    player_hand = deal_hand(player_deck)
    opp_hand    = deal_hand(opp_deck)

    display_hand(player_hand, "Your hand")

    player_action = _prompt_action()

    # ---- Player folds immediately ----------------------------------------
    if player_action == 'fold':
        print("\n  You folded.")
        display_hand(opp_hand, "Opponent had")
        opp.record_player_action('fold')
        score['opponent'] += 1
        print("  Opponent wins the round.")
        return

    # ---- Opponent responds -----------------------------------------------
    opp_action = opp.decide_action(opp_hand, player_action)

    if player_action == 'raise':
        if opp_action == 'fold':
            print("\n  Opponent folds. You win the round!")
            score['player'] += 1
            opp.record_player_action('raise')
            return
        else:
            print("\n  Opponent calls.")
            _showdown(player_hand, opp_hand, score)
            opp.record_player_action('raise')
            opp.record_showdown(player_hand, 'raise')
            return

    # player_action == 'check'
    if opp_action == 'raise':
        response = _prompt_call_or_fold()
        if response == 'fold':
            print("\n  You fold.")
            display_hand(opp_hand, "Opponent had")
            opp.record_player_action('fold')
            score['opponent'] += 1
            print("  Opponent wins the round.")
            return
        else:
            print("\n  You call.")
            _showdown(player_hand, opp_hand, score)
            opp.record_player_action('check')
            opp.record_showdown(player_hand, 'check')
            return

    # Both checked — go to showdown
    print("\n  Opponent checks.")
    _showdown(player_hand, opp_hand, score)
    opp.record_player_action('check')
    opp.record_showdown(player_hand, 'check')


# -----------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------

def main():
    print("=" * 52)
    print("              DRAFT  POKER")
    print("  Draft your deck. Read your opponent. Win.")
    print("=" * 52)

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

    for round_num in range(1, ROUNDS + 1):
        play_round(round_num, player_deck, opp_deck, opp, score)
        if round_num < ROUNDS:
            input("\n  Press Enter for the next round...")

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
