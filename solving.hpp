#pragma once
#include "parsing.hpp"
#include <cmath>
#include <iostream>
#include <utility>
#include <vector>



std::vector<std::pair<double, double>> h_approx_order_1(std::pair<double, double> initial_vals, double estimate_point, double step);

std::vector<std::vector<double>> h_approx_order_n(double x0, std::vector<double> initial_z, double estimate_point, double step);

