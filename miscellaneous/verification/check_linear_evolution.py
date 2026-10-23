"""Check the regional state and labelled-car formulas against literal moves.

Run from the repository root. The manuscript proof is a simultaneous induction;
these finite checks provide independent support for its formulas and indexing.
This script does not import the maintained simulator or alter experimental data.
Sites use Cartesian coordinates (x, y), with (1, 1) at the bottom left.
"""

import argparse
import json
from pathlib import Path


def displacement(n, y, cycle):
    start = 2 * n - 2 * y + 1
    release = 2 * n + y - 2
    if cycle < start:
        return 0
    if cycle < release:
        return (2 * (cycle - start + 1) + 2) // 3
    return cycle - 2 * n + y + 1


def predicted(n, time):
    north_cycle = (time + 1) // 2
    east_cycle = time // 2
    result = {}
    for y in range(1, n + 1):
        for x in range(1, n + 1):
            if x % 2 == 0:
                position = y + max(0, north_cycle - (2 * n - 2 * y + 1) + 1)
                if position <= n:
                    site = (x, position)
                    label = ("N", x, y)
                else:
                    continue
            else:
                if east_cycle and x + displacement(n, y, east_cycle - 1) >= n:
                    continue
                site = (x + displacement(n, y, east_cycle), y)
                label = ("E", x, y)
            if site in result:
                raise AssertionError(("predicted collision", n, time, site))
            if not all(1 <= coordinate <= n for coordinate in site):
                raise AssertionError(("predicted exterior car", n, time, site))
            result[site] = label
    return result


def literal_step(grid, n, time):
    selected = "N" if time % 2 else "E"
    moves = []
    for (x, y), label in grid.items():
        if label[0] != selected:
            continue
        destination = (x, y + 1) if selected == "N" else (x + 1, y)
        if destination not in grid:
            moves.append(((x, y), destination, label))
    result = grid.copy()
    for origin, _, _ in moves:
        del result[origin]
    for _, destination, label in moves:
        if all(1 <= coordinate <= n for coordinate in destination):
            if destination in result:
                raise AssertionError(("literal collision", destination))
            result[destination] = label
    return result


def regional_state(n, time):
    """Evaluate the piecewise periodic F_n directly, site by site."""
    q = (time - 1) // 2
    r = time // 2
    boundary = r - 2 * n + 3
    result = {}
    for y in range(1, n + 1):
        for x in range(1, n + 1):
            car = None
            if y >= boundary and 4 * y + time <= 4 * n - 2:
                car = "E" if x % 2 else "N"
            elif y >= boundary:
                if x % 2 == 0 and (y - n - q - 1) % 3 == 0:
                    car = "N"
                elif (3 * x - 4 * y >= time - 4 * n + 1
                      and ((x % 2 == 0 and (y - n - r + 1) % 3 == 0)
                           or (x % 2 == 1 and (y - n - r + 1) % 3 != 0))):
                    car = "E"
            elif x - y > r - 2 * n + 1 and (x - y - r) % 2 == 0:
                car = "E"
            if (n % 2 and x == n and r >= 1 and y >= boundary
                    and (r < 2 * n - 2 * y + 1 or (y - n - r) % 3 == 0)):
                car = None
            if car:
                result[x, y] = car
    return result


def check(max_n):
    observations = []
    checked_states = 0
    for n in range(1, max_n + 1):
        grid = {
            (x, y): ("N" if x % 2 == 0 else "E", x, y)
            for y in range(1, n + 1)
            for x in range(1, n + 1)
        }
        last_nonempty = 0
        for time in range(6 * n + 1):
            expected = predicted(n, time)
            if grid != expected:
                missing = set(expected.items()) - set(grid.items())
                extra = set(grid.items()) - set(expected.items())
                raise AssertionError((n, time, sorted(missing), sorted(extra)))
            actual_states = {site: label[0] for site, label in grid.items()}
            regional = regional_state(n, time)
            if regional != actual_states:
                raise AssertionError(("regional formula mismatch", n, time,
                                      sorted(set(regional.items()) - set(actual_states.items())),
                                      sorted(set(actual_states.items()) - set(regional.items()))))
            checked_states += 1
            if grid:
                last_nonempty = time
            grid = literal_step(grid, n, time + 1)
        clearing_time = last_nonempty + 1
        if clearing_time != 6 * n - 4:
            raise AssertionError(("wrong clearing time", n, clearing_time))
        observations.append({"n": n, "clearing_time": clearing_time})
    return {
        "method": "labelled literal simultaneous updates; no maintained simulator imports",
        "sizes": {"min": 1, "max": max_n, "count": max_n},
        "all_half_step_states_checked": checked_states,
        "coordinates": {"site_order": ["x", "y"], "origin": [1, 1],
                        "x_direction": "left to right", "y_direction": "bottom to top"},
        "north_first": True,
        "all_labelled_trajectories_match": True,
        "all_regional_states_match": True,
        "regional_formula_features": [
            "Final-region East parity is x-y-r even.",
            "For odd n, remove the last-column East car on blocked cycles after an East update.",
        ],
        "clearing_times": observations,
        "interpretation": "finite verification supports the separate all-n induction proof",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=40)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.max_n < 1:
        parser.error("--max-n must be positive")
    report = check(args.max_n)
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")
