"""
test_error.py — Error analysis for the RK4 ODE solver (main.exe)

Runs the compiled solver against ODEs with known analytical solutions,
measures absolute/relative error at y(x_end), and checks convergence order.
Also verifies that malformed equations produce a parse error.

Usage:
    python test_error.py
"""

import math
import os
import subprocess
import sys
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Executable discovery
# ---------------------------------------------------------------------------

_here = os.path.dirname(__file__)
_candidates = [
    os.path.join(_here, "build", "main.exe"),
    os.path.join(_here, "build", "Release", "main.exe"),
    os.path.join(_here, "main.exe"),
]
EXE_PATH = next((p for p in _candidates if os.path.isfile(p)), _candidates[0])

# ---------------------------------------------------------------------------
# Low-level runner
# ---------------------------------------------------------------------------

def _run_solver(stdin_data: str) -> subprocess.CompletedProcess:
    """Send stdin_data to the solver and return the CompletedProcess."""
    try:
        return subprocess.run(
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
        return subprocess.CompletedProcess([], -1, stdout="", stderr="TIMEOUT")


# ---------------------------------------------------------------------------
# High-level runners (used by accuracy tests)
# ---------------------------------------------------------------------------

def run_solver_order1(equation: str, x0: float, y0: float,
                      h: float, x_end: float) -> float | None:
    """Run a 1st-order ODE and return the y(x_end) estimate."""
    stdin_data = f"1\n{equation}\n{x0}\n{y0}\n{h}\n{x_end}\n"
    return _parse_y_from_result(_run_solver(stdin_data))


def run_solver_order_n(order: int, equation: str, x0: float,
                       z0: list[float], h: float, x_end: float) -> float | None:
    """Run an nth-order ODE and return the y(x_end) estimate.

    z0 must have exactly `order` entries: [y(x0), y'(x0), y''(x0), ...]
    """
    assert len(z0) == order, "z0 must have exactly `order` initial conditions"
    ic_lines = "\n".join(str(v) for v in z0)
    stdin_data = f"{order}\n{equation}\n{x0}\n{ic_lines}\n{h}\n{x_end}\n"
    return _parse_y_from_result(_run_solver(stdin_data))


def _parse_y_from_result(result: subprocess.CompletedProcess) -> float | None:
    """Extract the y value from solver output.

    1st-order: prints a plain float.
    nth-order: first line is "y(<x_end>) = <value>", followed by derivatives.
    """
    output = result.stdout.strip()
    if not output:
        print(f"ERROR: No output from solver.\nstderr: {result.stderr}")
        return None

    for line in output.splitlines():
        token = line.split("=")[-1].strip() if "=" in line else line.split()[-1]
        try:
            return float(token)
        except ValueError:
            continue

    print(f"ERROR: Could not parse solver output.\nFull output: {output!r}")
    return None


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def linreg(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Least-squares linear regression. Returns (slope, intercept)."""
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    if denom == 0:
        return (0.0, sy / n)
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    return slope, intercept


# ---------------------------------------------------------------------------
# Accuracy test: error table
# ---------------------------------------------------------------------------

def error_table(test_name: str,
                runner,           # callable(h) -> float | None
                x_end: float,
                exact_fn,         # callable(x) -> float
                step_sizes: list[float]) -> dict:
    """Print an error table across multiple step sizes and return a summary dict."""
    exact = exact_fn(x_end)
    print(f"\n{'='*74}")
    print(f"Test: {test_name}")
    print(f"  solve to x = {x_end}   |   exact y = {exact:.10f}")
    print(f"{'='*74}")
    print(f"  {'h':>10}  {'Abs Error':>14}  {'Rel Error %':>12}  "
          f"  {'Halving factor':>14}  {'Step order':>10}")
    print(f"  {'-'*10}  {'-'*14}  {'-'*12}  {'-'*16}  {'-'*10}")

    rows = []
    prev_err = None
    for h in step_sizes:
        approx = runner(h)
        if approx is None:
            print(f"  {h:>10.6f}  {'FAILED':>14}")
            prev_err = None
            continue

        abs_err = abs(approx - exact)
        rel_err = abs_err / abs(exact) if abs(exact) > 1e-10 else float("inf")
        rows.append((h, abs_err, rel_err))

        if prev_err is not None and abs_err > 0 and prev_err > 0:
            factor = prev_err / abs_err
            factor_str = f"{factor:14.2f}x"
            order_str  = f"{math.log2(factor):10.2f}"
        else:
            factor_str = f"{'—':>15}"
            order_str  = f"{'—':>10}"

        print(f"  {h:>10.6f}  {abs_err:>14.6e}  {rel_err*100:>11.4f}%"
              f"  {factor_str}  {order_str}")
        prev_err = abs_err

    # Fit error ~ C * h^p via log-log linear regression
    valid = [(h, e) for h, e, _ in rows if e > 0]
    fitted_order = fitted_C = None
    if len(valid) >= 2:
        log_h = [math.log(h) for h, _ in valid]
        log_e = [math.log(e) for _, e in valid]
        fitted_order, log_C = linreg(log_h, log_e)
        fitted_C = math.exp(log_C)

    rel_errors    = [r for _, _, r in rows if r != float("inf")]
    mean_rel_pct  = sum(rel_errors) / len(rel_errors) * 100 if rel_errors else float("nan")
    total_rel_pct = sum(rel_errors) * 100
    total_abs     = sum(e for _, e, _ in rows)

    print(f"  {'-'*10}  {'-'*14}  {'-'*12}  {'-'*16}  {'-'*10}")
    if fitted_order is not None:
        print(f"  Fitted error model:  error ~ {fitted_C:.4e} * h^{fitted_order:.3f}"
              f"   (ideal RK4: h^4.000)")
        print(f"  When h is halved:    error shrinks by ~{2**fitted_order:.1f}x"
              f"   (ideal RK4: {2**4}x)")
    print(f"  Total abs error (sum over step sizes):   {total_abs:.6e}")
    print(f"  Mean  rel error (avg  over step sizes):  {mean_rel_pct:.4f}%")
    print(f"  Total rel error (sum  over step sizes):  {total_rel_pct:.4f}%")
    print()

    return {
        "name":          test_name,
        "fitted_order":  fitted_order,
        "fitted_C":      fitted_C,
        "total_abs":     total_abs,
        "mean_rel_pct":  mean_rel_pct,
        "total_rel_pct": total_rel_pct,
    }


# ---------------------------------------------------------------------------
# Accuracy test cases
# ---------------------------------------------------------------------------

ORDER1_CASES = [
    {
        "name":   "1st order | dy/dx = y,          y(0)=1    ->  y = e^x",
        "runner": lambda h: run_solver_order1("y",            0.0, 1.0, h, 1.0),
        "x_end":  1.0,
        "exact":  lambda x: math.exp(x),
    },
    {
        "name":   "1st order | dy/dx = -y,          y(0)=1    ->  y = e^(-x)",
        "runner": lambda h: run_solver_order1("-y",            0.0, 1.0, h, 1.0),
        "x_end":  1.0,
        "exact":  lambda x: math.exp(-x),
    },
    {
        "name":   "1st order | dy/dx = 2*x,         y(0)=0    ->  y = x^2",
        "runner": lambda h: run_solver_order1("2*x",           0.0, 0.0, h, 2.0),
        "x_end":  2.0,
        "exact":  lambda x: x**2,
    },
    {
        "name":   "1st order | dy/dx = y - x^2 + 1, y(0)=0.5 ->  y = (x+1)^2 - 0.5*e^x",
        "runner": lambda h: run_solver_order1("y - x^2 + 1",  0.0, 0.5, h, 2.0),
        "x_end":  2.0,
        "exact":  lambda x: (x + 1)**2 - 0.5 * math.exp(x),
    },
]

# y0=y, y1=y', y2=y'', ...
ORDER2_CASES = [
    {
        "name":   "2nd order | y'' = -y,          y(0)=0, y'(0)=1  ->  y = sin(x)",
        "runner": lambda h: run_solver_order_n(2, "-y0",         0.0, [0.0, 1.0],  h, 1.0),
        "x_end":  1.0,
        "exact":  lambda x: math.sin(x),
    },
    {
        "name":   "2nd order | y'' = -y,          y(0)=1, y'(0)=0  ->  y = cos(x)",
        "runner": lambda h: run_solver_order_n(2, "-y0",         0.0, [1.0, 0.0],  h, 1.0),
        "x_end":  1.0,
        "exact":  lambda x: math.cos(x),
    },
    {
        "name":   "2nd order | y'' = y,           y(0)=1, y'(0)=1  ->  y = e^x",
        "runner": lambda h: run_solver_order_n(2, "y0",          0.0, [1.0, 1.0],  h, 1.0),
        "x_end":  1.0,
        "exact":  lambda x: math.exp(x),
    },
    {
        "name":   "2nd order | y'' = -2y' - y,   y(0)=1, y'(0)=-1 ->  y = e^(-x)",
        "runner": lambda h: run_solver_order_n(2, "-2*y1 - y0",  0.0, [1.0, -1.0], h, 2.0),
        "x_end":  2.0,
        "exact":  lambda x: math.exp(-x),
    },
]

ORDER3_CASES = [
    {
        "name":   "3rd order | y''' = y,  y(0)=1,y'(0)=1,y''(0)=1  ->  y = e^x",
        "runner": lambda h: run_solver_order_n(3, "y0",  0.0, [1.0, 1.0, 1.0], h, 1.0),
        "x_end":  1.0,
        "exact":  lambda x: math.exp(x),
    },
    {
        "name":   "3rd order | y''' = -y', y(0)=0,y'(0)=1,y''(0)=0 ->  y = sin(x)",
        "runner": lambda h: run_solver_order_n(3, "-y1", 0.0, [0.0, 1.0, 0.0], h, 1.0),
        "x_end":  1.0,
        "exact":  lambda x: math.sin(x),
    },
]

ORDER4_CASES = [
    {
        "name":   "4th order | y'''' = y, y(0..3)=1  ->  y = e^x",
        "runner": lambda h: run_solver_order_n(4, "y0", 0.0, [1.0, 1.0, 1.0, 1.0], h, 1.0),
        "x_end":  1.0,
        "exact":  lambda x: math.exp(x),
    },
]

STEP_SIZES = [0.2, 0.1, 0.05, 0.025, 0.0125]


# ---------------------------------------------------------------------------
# Parse-error test cases
# ---------------------------------------------------------------------------

class ParseCase(NamedTuple):
    description:     str   # human-readable label
    stdin_data:      str   # complete input fed to the solver
    expected_stderr: str   # fragment that must appear in stderr on failure


def _stdin_order1(eq: str) -> str:
    return f"1\n{eq}\n0.0\n1.0\n0.1\n1.0\n"

def _stdin_order2(eq: str) -> str:
    return f"2\n{eq}\n0.0\n1.0\n0.0\n0.1\n1.0\n"


PARSE_ERROR_CASES: list[ParseCase] = [
    # 1st-order bad equations (expected stderr: "parse error")
    ParseCase("1st order | unmatched paren:    'y + ('",        _stdin_order1("y + ("),  "parse error"),
    ParseCase("1st order | bare operator:      '+'",            _stdin_order1("+"),       "parse error"),
    ParseCase("1st order | invalid symbols:    '$$$'",          _stdin_order1("$$$"),     "parse error"),
    ParseCase("1st order | unknown variable:   'z' (not x,y)",  _stdin_order1("z"),       "parse error"),
    ParseCase("1st order | double operator:    'y ++ x'",       _stdin_order1("y ++ x"), "parse error"),
    ParseCase("1st order | empty equation",                     _stdin_order1(""),        "parse error"),

    # 2nd-order bad equations (expected stderr: "nth order parse error")
    ParseCase("2nd order | unmatched paren:    'y0 + ('",       _stdin_order2("y0 + ("), "nth order parse error"),
    ParseCase("2nd order | invalid symbols:    '@@@'",          _stdin_order2("@@@"),     "nth order parse error"),
    ParseCase("2nd order | wrong variable:     'y' (not y0,y1)",_stdin_order2("y"),       "nth order parse error"),
    ParseCase("2nd order | bare operator:      '*'",            _stdin_order2("*"),       "nth order parse error"),
]


def run_parse_error_tests() -> None:
    """Run every ParseCase and print PASS/FAIL with diagnostics on failure."""
    print(f"\n{'#'*74}")
    print("PARSE ERROR TESTS")
    print(f"{'#'*74}")
    print(f"  {'Test':<62}  Result")
    print(f"  {'-'*62}  ------")

    passed = failed = 0
    for case in PARSE_ERROR_CASES:
        result = _run_solver(case.stdin_data)
        ok = case.expected_stderr in result.stderr

        status = "PASS" if ok else "FAIL"
        print(f"  {case.description[:62]:<62}  {status}")

        if not ok:
            got = repr(result.stderr[:120]) if result.stderr else repr(result.stdout[:120])
            print(f"    expected in stderr: {case.expected_stderr!r}")
            print(f"    got stderr:         {got}")

        passed += ok
        failed += not ok

    print(f"  {'-'*62}  ------")
    print(f"  {passed} passed, {failed} failed  ({len(PARSE_ERROR_CASES)} total)\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_group(group_title: str, cases: list[dict]) -> list[dict]:
    print(f"\n{'#'*74}")
    print(group_title)
    print(f"{'#'*74}")
    return [
        error_table(
            test_name=tc["name"],
            runner=tc["runner"],
            x_end=tc["x_end"],
            exact_fn=tc["exact"],
            step_sizes=STEP_SIZES,
        )
        for tc in cases
    ]


def print_summary(summaries: list[dict]) -> None:
    print(f"\n{'#'*74}")
    print("GLOBAL SUMMARY")
    print(f"{'#'*74}")
    print(f"  {'Test':>55}  {'Order (fitted)':>14}  {'Mean err %':>10}  {'Total err %':>11}")
    print(f"  {'-'*55}  {'-'*14}  {'-'*10}  {'-'*11}")

    for s in summaries:
        order_s    = f"{s['fitted_order']:.3f}" if s["fitted_order"] is not None else "N/A"
        mean_s     = f"{s['mean_rel_pct']:>9.4f}%" if not math.isnan(s["mean_rel_pct"]) else f"{'N/A':>10}"
        total_s    = f"{s['total_rel_pct']:>10.4f}%" if not math.isnan(s["mean_rel_pct"]) else f"{'N/A':>11}"
        print(f"  {s['name'][:55]:<55}  {order_s:>14}  {mean_s}  {total_s}")

    valid_orders      = [s["fitted_order"] for s in summaries if s["fitted_order"] is not None]
    avg_order         = sum(valid_orders) / len(valid_orders) if valid_orders else float("nan")
    valid_mean        = [s["mean_rel_pct"]  for s in summaries if not math.isnan(s["mean_rel_pct"])]
    overall_mean_pct  = sum(valid_mean) / len(valid_mean) if valid_mean else float("nan")
    overall_total_pct = sum(s["total_rel_pct"] for s in summaries if not math.isnan(s["total_rel_pct"]))

    print(f"  {'-'*55}  {'-'*14}  {'-'*10}  {'-'*11}")
    mean_s = f"{overall_mean_pct:>9.4f}%" if not math.isnan(overall_mean_pct) else f"{'N/A':>10}"
    print(f"  {'Average / Grand total':<55}  {avg_order:>14.3f}  {mean_s}  {overall_total_pct:>10.4f}%")
    print()
    print(f"  Ideal RK4 convergence order: 4.000  (error shrinks 16x each time h is halved)")
    print(f"  Observed avg order:          {avg_order:.3f}")
    if avg_order < 3.5:
        print(f"  --> Order is {4.0 - avg_order:.2f} below ideal. A bug may be degrading the method.")
    else:
        print(f"  --> Order is close to ideal. Implementation looks correct.")
    print()


def main() -> None:
    print("RK4 Solver Error Analysis  (1st through 4th order)")
    print(f"Executable : {EXE_PATH}")
    print(f"Step sizes : {STEP_SIZES}")

    run_parse_error_tests()

    all_summaries  = run_group("1ST-ORDER ODEs", ORDER1_CASES)
    all_summaries += run_group("2ND-ORDER ODEs", ORDER2_CASES)
    all_summaries += run_group("3RD-ORDER ODEs", ORDER3_CASES)
    all_summaries += run_group("4TH-ORDER ODEs", ORDER4_CASES)

    print_summary(all_summaries)


if __name__ == "__main__":
    main()
