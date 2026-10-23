"""Exhaustively check the Top Row Model and its update-map identities.

This is a finite check of the exact identities in the arbitrary-n proof.
States are columns from left to right; a nonempty column j stores entries with
row indices i>=j. No maintained simulation code is imported.
"""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path


def valid(state):
    n = len(state)
    return all(not stack or len(stack) == n - j and set(stack) <= {2, 4}
               for j, stack in enumerate(state))


def shift(state, j):
    if not state[j] or j + 1 < len(state) and state[j + 1]:
        return state
    result = list(state)
    result[j] = ()
    if j + 1 < len(state):
        result[j + 1] = state[j][1:]
    return tuple(result)


def reduce_entry(state, i, j):
    if not state[j] or state[j][i - j] != 4:
        return state
    result = list(state)
    column = list(state[j])
    column[i - j] = 2
    result[j] = tuple(column)
    return tuple(result)


def update(state):
    n = len(state)
    result = [()] * n
    for j, stack in enumerate(state):
        if not stack:
            continue
        if j + 1 < n and state[j + 1]:
            destination, contents = j, stack
        elif stack[0] == 4:
            destination, contents = j, (2,) + stack[1:]
        elif j + 1 < n:
            destination, contents = j + 1, stack[1:]
        else:
            continue
        if result[destination]:
            raise AssertionError(("collision", state, destination))
        result[destination] = contents
    result = tuple(result)
    assert valid(result), ("invalid update", state, result)
    return result


def potential(state):
    return sum(sum(stack) for stack in state)


def check_potential(before, after):
    assert valid(after), ("invalid map", before, after)
    assert before == after or potential(before) > potential(after)


def compare_shift_case(state, j):
    following = shift(state, j)
    if following == state:
        return "identity"
    upper, lower = update(state), update(following)
    b = state[j][0]
    right_occupied = j + 2 < len(state) and bool(state[j + 2])
    case = "exit" if j + 1 == len(state) else str((b, state[j][1], right_occupied))
    if j + 1 == len(state):
        if b == 4:
            upper = shift(upper, j)
    elif right_occupied:
        if b == 4:
            upper = shift(upper, j)
    else:
        c = state[j][1]
        if b == 4:
            upper = shift(upper, j)
        if c == 4:
            upper = reduce_entry(upper, j + 1, j + 1)
        else:
            upper = shift(upper, j + 1)
    if j and state[j - 1]:
        if state[j - 1][0] == 4:
            upper = reduce_entry(upper, j - 1, j - 1)
        else:
            upper = shift(upper, j - 1)
    assert upper == lower, ("false shift identity", state, j, upper, lower)
    return case


def compare_reduction_case(state, i, j):
    following = reduce_entry(state, i, j)
    if following == state:
        return "identity"
    upper, lower = update(state), update(following)
    blocked = j + 1 < len(state) and bool(state[j + 1])
    if i == j:
        if blocked:
            upper = reduce_entry(upper, i, j)
            case = "diagonal blocked"
        else:
            upper = shift(upper, j)
            case = "diagonal free"
    elif not blocked and state[j][0] == 2:
        upper = reduce_entry(upper, i, j + 1)
        case = "off diagonal moves"
    else:
        upper = reduce_entry(upper, i, j)
        case = "off diagonal stays"
    assert upper == lower, ("false reduction identity", state, i, j, upper, lower)
    return case


def construct_from_greatest(target):
    n = len(target)
    state = tuple((4,) * (n - j) for j in range(n))
    occupied = [j for j, stack in enumerate(target) if stack]
    m = len(occupied)
    for original in range(n - 1, m - 1, -1):
        for j in range(original, n):
            state = shift(state, j)
    for original in range(m - 1, -1, -1):
        for j in range(original, occupied[original]):
            state = shift(state, j)
    for j, stack in enumerate(target):
        for offset, entry in enumerate(stack):
            if entry == 2:
                state = reduce_entry(state, j + offset, j)
    assert state == target, ("greatest state construction", state, target)


def verify(max_n):
    reports = []
    for n in range(1, max_n + 1):
        columns = [[()] + list(product((2, 4), repeat=n - j)) for j in range(n)]
        shifts, reductions = Counter(), Counter()
        states = maximum = 0
        for state in product(*columns):
            assert valid(state)
            states += 1
            construct_from_greatest(state)
            for j in range(n):
                check_potential(state, shift(state, j))
                shifts[compare_shift_case(state, j)] += 1
                for i in range(j, n):
                    check_potential(state, reduce_entry(state, i, j))
                    reductions[compare_reduction_case(state, i, j)] += 1
            moving = state
            half_steps = 0
            while any(moving):
                moving = update(moving)
                half_steps += 2
                assert half_steps <= 8 * n - 4, ("bound exceeded", n, state)
            maximum = max(maximum, half_steps)
        greatest = tuple((4,) * (n - j) for j in range(n))
        moving, greatest_time = greatest, 0
        while any(moving):
            moving = update(moving)
            greatest_time += 2
        assert greatest_time == maximum == 8 * n - 4
        reports.append({
            "n": n,
            "valid_states_checked": states,
            "shift_map_cases": dict(sorted(shifts.items())),
            "reduction_map_cases": dict(sorted(reductions.items())),
            "maximum_clearing_time": maximum,
            "greatest_state_clearing_time": greatest_time,
        })
    return {
        "model": "matrix-stack Top Row Model",
        "all_exact_map_identities_pass": True,
        "all_map_outputs_valid": True,
        "nonidentity_maps_strictly_decrease_entry_sum": True,
        "all_states_constructed_from_greatest_by_maps": True,
        "interpretation": "finite verification supports the separate arbitrary-n case proof",
        "checks": reports,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.max_n < 1:
        parser.error("--max-n must be positive")
    report = json.dumps(verify(args.max_n), indent=2) + "\n"
    if args.output:
        args.output.write_text(report)
    else:
        print(report, end="")
