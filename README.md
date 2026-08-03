# Differential Equations Solver & Visualizer

A C++ command-line tool that numerically solves ODEs using 4th-order Runge-Kutta (RK4), then plots the solution in a native window.

- **1st-order ODEs**: `dy/dx = f(x, y)`
- **nth-order ODEs**: `y^(n) = f(x, y, y', y'', ...)`, reduced internally to a first-order system

Equations are typed in as plain math expressions (parsed with [exprtk](https://github.com/ArashPartow/exprtk)) — no recompiling needed to try a new equation.

## Features

- RK4 solver for arbitrary-order ODEs
- Full solution trajectory (not just the final value) written to `trajectory.csv`
- Native plot window via [MathGL](http://mathgl.sourceforge.net/) — single curve for 1st-order, one curve per derivative for nth-order

## Requirements

Built and tested with [MSYS2](https://www.msys2.org/) UCRT64 on Windows.

```
pacman -S mingw-w64-ucrt-x86_64-gcc \
          mingw-w64-ucrt-x86_64-cmake \
          mingw-w64-ucrt-x86_64-mathgl
```

`exprtk.hpp` is already vendored in the repo — no separate install needed.

## Build

```
cmake -S . -B build -G "MinGW Makefiles"
cmake --build build
```

## Run

`main.exe` needs `ucrt64/bin` on `PATH` at runtime (for the MathGL/GLUT DLLs):

```
$env:PATH = "C:\msys64\ucrt64\bin;$env:PATH"   # PowerShell
cd build
.\main.exe
```

### Example: 1st-order ODE

```
ODE order: 1
dy/dx = x + y
initial x = 0
initial y = 1
step = 0.01
input what x value you want to estimate = 2
```

### Example: nth-order ODE (damped harmonic oscillator, y'' = -y - 0.3y')

Variables are `x` and `y0, y1, ..., y{order-1}`, where `y0 = y`, `y1 = y'`, etc.

```
ODE order: 2
f = -y0 - 0.3*y1
initial x = 0
y^(0)(0) = 1
y^(1)(0) = 0
step = 0.01
input what x value you want to estimate = 10
```

Equations accept standard exprtk syntax: `+ - * / ^`, `sin`, `cos`, `exp`, `sqrt`, `log`, `pi`, etc.

After solving, the program prints the estimate, writes the full trajectory to `trajectory.csv`, and opens a MathGL window with the plotted curve(s).

## Project layout

| File | Purpose |
|---|---|
| `main.cpp` | CLI entry point — collects input, drives the solve/print/plot pipeline |
| `parsing.hpp/.cpp` | Wraps exprtk to compile and evaluate the user's equation |
| `solving.hpp/.cpp` | RK4 integrator, returns the full solution trajectory |
| `visualizer.hpp/.cpp` | Opens a MathGL window and plots the trajectory |
| `test_error.py` | Error/convergence tests against ODEs with known analytical solutions |