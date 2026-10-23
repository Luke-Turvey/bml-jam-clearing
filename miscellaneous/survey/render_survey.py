"""Render the recorded periodic-tile survey as a catalogue of diagrams."""

from fractions import Fraction
from itertools import product
import math
from pathlib import Path


def _fraction(value):
    if isinstance(value, dict):
        return Fraction(value["numerator"], value["denominator"])
    return Fraction(value)


def _tex_fraction(value):
    value = _fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    sign = "-" if value < 0 else ""
    return sign + r"\frac{" + str(abs(value.numerator)) + "}{" + str(value.denominator) + "}"


def _tex_decimal(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("power-law coefficients must be finite")
    result = format(value, ".3g")
    if "e" in result:
        coefficient, exponent = result.split("e")
        return coefficient + r"\times10^{" + str(int(exponent)) + "}"
    return result


def _linear_term(value):
    value = _fraction(value)
    if value == 0:
        return "0"
    if value == 1:
        return "n"
    if value == -1:
        return "-n"
    return _tex_fraction(value) + "n"


def _affine_formula(slope, intercept):
    slope, intercept = _fraction(slope), _fraction(intercept)
    result = _linear_term(slope)
    if not slope:
        return _tex_fraction(intercept)
    if intercept:
        result += ("+" if intercept > 0 else "-") + _tex_fraction(abs(intercept))
    return result


def _candidate(record):
    candidate = record.get("affine_periodic_candidate")
    if candidate and candidate.get("validated"):
        period = candidate["period_in_sample_index"]
        if not isinstance(period, int) or period < 1 or len(candidate["offsets"]) != period:
            raise ValueError(f"invalid periodic model for tile {record['tile']}")
        if (candidate.get("sample_anchor", 0) != 0
                or candidate.get("q_definition", "n/3") not in {"n/3", "q=n/3"}):
            raise ValueError(f"unsupported periodic phase for tile {record['tile']}")
        return candidate
    return None


def _tile_diagram(tile):
    lines = [r"\resizebox{.96\linewidth}{!}{%", r"\begin{tikzpicture}"]
    for row in range(3):
        for column in range(3):
            command = r"\rc" if tile[3 * row + column] == "1" else r"\uc"
            # The source tile is row major, with the first row at the top.
            x = ("0", "0.6", "1.2")[column]
            y = ("0", "-0.6", "-1.2")[row]
            lines.append(command + "{" + x + "}{" + y + "}")
    lines.extend([r"\end{tikzpicture}%", r"}"])
    return lines


def _card(record):
    tile = record["tile"]
    lines = ["% Tiling " + tile,
             r"\begin{minipage}[t]{.19\linewidth}\centering\vspace{0pt}"]
    lines.extend(_tile_diagram(tile))
    lines.append(r"\par\smallskip")
    candidate = _candidate(record)
    if candidate is None:
        fit = record["fits"]["100"]
        coefficient = fit.get("coefficient", 2 ** fit["intercept"])
        formula = (r"T\approx " + _tex_decimal(coefficient)
                   + "n^{" + format(float(fit["power"]), ".3f") + "}")
    elif candidate["period_in_sample_index"] == 1:
        formula = "T=" + _affine_formula(candidate["slope"], candidate["offsets"][0])
    else:
        formula = "T=" + _linear_term(candidate["slope"]) + r"+P(n)"
    lines.append(r"{\small\(" + formula + r"\)\par}")
    lines.append(r"\end{minipage}")
    return lines


def _catalogue_rows(records):
    lines = []
    for start in range(0, len(records), 5):
        lines.append(r"\noindent")
        for column, record in enumerate(records[start:start + 5]):
            if column:
                lines.append(r"\hfill")
            lines.extend(_card(record))
        lines.append(r"\par\vspace{.6em}")
    return lines


def render_tex(summary):
    """Collect the observed affine, periodic and fitted power formulas."""
    records = sorted(summary["records"], key=lambda record: record["tile"])
    tiles = [record["tile"] for record in records]
    expected = {"".join(tile) for tile in product("13", repeat=9)}
    if len(tiles) != 512 or set(tiles) != expected:
        raise ValueError("the diagram catalogue requires each of the 512 tiles exactly once")
    protocol = summary["affine_periodic_analysis"]
    training, validation = protocol["training"], protocol["validation"]
    selected = [record for record in records if _candidate(record) is not None]
    power_records = [record for record in records if _candidate(record) is None]
    power_fit = protocol["power_fit"]
    lines = [
        r"\section{Clearing formulas for periodic tilings}\label{app:survey}",
        r"The catalogue gives observed clearing formulas and conjectured power laws",
        r"for all $512$ $3$-periodic tilings, where $T=T(W_n,n)$ and $n$ is a multiple of $3$.",
        r"Red cells contain East cars and blue cells North cars.",
        "",
        r"\subsection{Affine and periodic formulas}",
        f"The following ${len(selected)}$ $3$-periodic tilings have affine or linear-plus-periodic",
        r"clearing formulas in the recorded data, where $P$ denotes",
        r"a periodic function that may depend on the tiling.",
        "The formulas were determined using",
        f"${training['minimum_n']}\\leq n\\leq{training['maximum_n']}$ "
        "and checked at every",
        f"${validation['minimum_n']}\\leq n\\leq{validation['maximum_n']}$, with $n$ a multiple of $3$.",
        "",
        r"The linear coefficient $a$ is obtained from constant increments over repeated cycles,",
        r"giving the observed bound $T\leq an+\max P$.",
        r"A periodic correction is accepted when $T-an$ repeats on the fitting sizes",
        r"and agrees exactly with the validation data.",
        r"The formulas describe the tested sizes.",
        "",
    ]
    lines.extend(_catalogue_rows(selected))
    lines.extend([
        "",
        r"\subsection{Conjectured power laws}",
        f"For the remaining ${len(power_records)}$ tilings, the formulas $T\\approx Cn^\\alpha$",
        r"are fitted by ordinary least squares in $\log_2 T=\alpha\log_2 n+\log_2 C$",
        f"over ${power_fit['minimum_n']}\\leq n\\leq{power_fit['maximum_n']}$.",
        "",
    ])
    lines.extend(_catalogue_rows(power_records))
    return "\n".join(lines) + "\n"


def write_tex(summary, destination):
    """Write the diagram catalogue without modifying measurements or analysis."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_tex(summary))
