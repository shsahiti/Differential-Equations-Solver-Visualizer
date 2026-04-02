"""
test_error.py — Error analysis for the RK4 ODE solver (main.exe)

Runs the compiled solver against ODEs with known analytical solutions,
measures absolute/relative error, and checks convergence order.

Usage:
    python test_error.py
"""

import subprocess
import math
import sys
import os

_here = os.path.dirname(__file__)
# Prefer the cmake build output; fall back to a legacy root-level binary
_candidates = [
    os.path.join(_here, "build", "main.exe"),           # NMake / Ninja
    os.path.join(_here, "build", "Release", "main.exe"), # VS generator
    os.path.join(_here, "main.exe"),                     # legacy MSVC direct build
]
EXE_PATH = next((p for p in _candidates if os.path.isfile(p)), _candidates[0])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_solver(equation: str, x0: float, y0: float, h: float, x_end: float) -> float | None:
    """Send inputs to main.exe via stdin and return the printed result."""
    stdin_data = f"{equation}\n{x0}\n{y0}\n{h}\n{x_end}\n"
    try:
        result = subprocess.run(
            [EXE_PATH],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        print(f"ERROR: Could not find executable at {EXE_PATH}")
        print("       Build the project first (Ctrl+Shift+B in VS Code).")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("ERROR: Solver timed out.")
        return None

    # The exe prints all prompts inline; the numeric answer is the last whitespace-
    # separated token in the entire stdout (e.g. "dy/dx = ... = 2.71828").
    output = result.stdout.strip()
    if not output:
        print(f"ERROR: No output from solver.\nstderr: {result.stderr}")
        return None
    last_token = output.split()[-1]
    try:
        return float(last_token)
    except ValueError:
        print(f"ERROR: Could not parse solver output: {last_token!r}\nFull output: {output!r}")
        return None


def linreg(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Least-squares linear regression. Returns (slope, intercept)."""
    n = len(xs)
    sx = sum(xs); sy = sum(ys)
    sxx = sum(x*x for x in xs); sxy = sum(x*y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    if denom == 0:
        return (0.0, sy / n)
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    return slope, intercept


def error_table(test_name: str,
                equation: str,
                x0: float, y0: float,
                x_end: float,
                exact_fn,
                step_sizes: list[float]) -> dict:
    """
    Print an error table for a single test case across multiple step sizes.
    Returns a summary dict for use in the global report.
    """
    exact = exact_fn(x_end)
    print(f"\n{'='*74}")
    print(f"Test: {test_name}")
    print(f"  dy/dx = {equation}")
    print(f"  y({x0}) = {y0},  solve to x = {x_end}   |   exact = {exact:.10f}")
    print(f"{'='*74}")
    print(f"  {'h':>10}  {'Abs Error':>14}  {'Rel Error %':>12}  "
          f"  {'Halving factor':>14}  {'Step order':>10}")
    print(f"  {'-'*10}  {'-'*14}  {'-'*12}  {'-'*16}  {'-'*10}")

    rows = []   # (h, abs_err, rel_err)
    prev_err = None
    for h in step_sizes:
        approx = run_solver(equation, x0, y0, h, x_end)
        if approx is None:
            print(f"  {h:>10.6f}  {'FAILED':>14}")
            prev_err = None
            continue
        abs_err = abs(approx - exact)
        rel_err = abs_err / abs(exact) if exact != 0 else float("inf")
        rows.append((h, abs_err, rel_err))

        if prev_err is not None and abs_err > 0 and prev_err > 0:
            factor = prev_err / abs_err          # actual reduction when h halved
            order  = math.log2(factor)
            factor_str = f"{factor:14.2f}x"
            order_str  = f"{order:10.2f}"
        else:
            factor_str = f"{'—':>15}"
            order_str  = f"{'—':>10}"

        print(f"  {h:>10.6f}  {abs_err:>14.6e}  {rel_err*100:>11.4f}%"
              f"  {factor_str}  {order_str}")
        prev_err = abs_err

    # --- Fitted model:  error = C * h^p  via log-log regression ---
    valid = [(h, e) for h, e, _ in rows if e > 0]
    fitted_order = fitted_C = None
    if len(valid) >= 2:
        log_h = [math.log(h) for h, _ in valid]
        log_e = [math.log(e) for _, e in valid]
        fitted_order, log_C = linreg(log_h, log_e)
        fitted_C = math.exp(log_C)

    # --- Per-test summary stats ---
    rel_errors = [r for _, _, r in rows if r != float("inf")]
    mean_rel_pct  = sum(rel_errors) / len(rel_errors) * 100 if rel_errors else float("nan")
    total_rel_pct = sum(rel_errors) * 100
    abs_errors    = [e for _, e, _ in rows]
    total_abs     = sum(abs_errors)

    print(f"  {'-'*10}  {'-'*14}  {'-'*12}  {'-'*16}  {'-'*10}")
    if fitted_order is not None:
        print(f"  Fitted error model:  error ~ {fitted_C:.4e} * h^{fitted_order:.3f}"
              f"   (ideal RK4: h^4.000)")
        ideal_factor = 2 ** 4
        print(f"  When h is halved:    error shrinks by ~{2**fitted_order:.1f}x"
              f"   (ideal RK4: {ideal_factor}x)")
    print(f"  Total abs error (sum over step sizes):   {total_abs:.6e}")
    print(f"  Mean  rel error (avg  over step sizes):  {mean_rel_pct:.4f}%")
    print(f"  Total rel error (sum  over step sizes):  {total_rel_pct:.4f}%")
    print()

    return {
        "name": test_name,
        "fitted_order": fitted_order,
        "fitted_C": fitted_C,
        "total_abs": total_abs,
        "mean_rel_pct": mean_rel_pct,
        "total_rel_pct": total_rel_pct,
    }


# ---------------------------------------------------------------------------
# Test cases  (dy/dx = f(x,y), exact solution y(x))
# ---------------------------------------------------------------------------

TEST_CASES = [
    {
        "name": "Exponential growth   dy/dx = y,  y(0)=1  ->  y=e^x",
        "equation": "y",
        "x0": 0.0, "y0": 1.0,
        "x_end": 1.0,
        "exact": lambda x: math.exp(x),
    },
    {
        "name": "Exponential decay    dy/dx = -y, y(0)=1  ->  y=e^(-x)",
        "equation": "-y",
        "x0": 0.0, "y0": 1.0,
        "x_end": 1.0,
        "exact": lambda x: math.exp(-x),
    },
    {
        "name": "Quadratic solution   dy/dx = 2*x, y(0)=0  ->  y=x^2",
        "equation": "2*x",
        "x0": 0.0, "y0": 0.0,
        "x_end": 2.0,
        "exact": lambda x: x**2,
    },
    {
        "name": "Classic RK4 test     dy/dx = y - x^2 + 1, y(0)=0.5  ->  y=(x+1)^2 - 0.5*e^x",
        "equation": "y - x^2 + 1",
        "x0": 0.0, "y0": 0.5,
        "x_end": 2.0,
        "exact": lambda x: (x + 1)**2 - 0.5 * math.exp(x),
    },
]

STEP_SIZES = [0.2, 0.1, 0.05, 0.025, 0.0125]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("RK4 Solver Error Analysis")
    print(f"Executable: {EXE_PATH}")
    print(f"Step sizes tested: {STEP_SIZES}")

    summaries = []
    for tc in TEST_CASES:
        s = error_table(
            test_name=tc["name"],
            equation=tc["equation"],
            x0=tc["x0"], y0=tc["y0"],
            x_end=tc["x_end"],
            exact_fn=tc["exact"],
            step_sizes=STEP_SIZES,
        )
        summaries.append(s)

    # -----------------------------------------------------------------------
    # Global summary across all test cases
    # -----------------------------------------------------------------------
    print(f"\n{'#'*74}")
    print("GLOBAL SUMMARY")
    print(f"{'#'*74}")
    print(f"  {'Test':>50}  {'Order (fitted)':>14}  {'Mean err %':>10}  {'Total err %':>11}")
    print(f"  {'-'*50}  {'-'*14}  {'-'*10}  {'-'*11}")
    for s in summaries:
        short = s["name"][:50]
        order_s = f"{s['fitted_order']:.3f}" if s["fitted_order"] is not None else "N/A"
        print(f"  {short:<50}  {order_s:>14}  {s['mean_rel_pct']:>9.4f}%  {s['total_rel_pct']:>10.4f}%")

    valid_orders = [s["fitted_order"] for s in summaries if s["fitted_order"] is not None]
    avg_order = sum(valid_orders) / len(valid_orders) if valid_orders else float("nan")
    overall_mean_pct  = sum(s["mean_rel_pct"]  for s in summaries) / len(summaries)
    overall_total_pct = sum(s["total_rel_pct"] for s in summaries)

    print(f"  {'-'*50}  {'-'*14}  {'-'*10}  {'-'*11}")
    print(f"  {'Average / Grand total':<50}  {avg_order:>14.3f}  {overall_mean_pct:>9.4f}%  {overall_total_pct:>10.4f}%")
    print()
    print(f"  Ideal RK4 convergence order: 4.000  (error halves by 16x each time h is halved)")
    print(f"  Observed avg order:          {avg_order:.3f}")
    if avg_order < 3.5:
        gap = 4.0 - avg_order
        print(f"  --> Order is {gap:.2f} below ideal. A bug is likely degrading the method.")
    else:
        print(f"  --> Order is close to ideal. Implementation looks correct.")
    print()


if __name__ == "__main__":
    main()
