#pragma once
#include <string>
#include <iostream>
#include <vector>

void seprable_input(const std::string& function);
double eval_function(double x, double y);


void nth_order_input(const std::string& function, int order);
double eval_nth_order(double x_val, const std::vector<double>& z_vals);