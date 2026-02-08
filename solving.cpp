#include "solving.hpp"
#include <cmath>
#include <iostream>
#include "parsing.hpp"

double h_approx_order_1(std::pair<double, double> initial_vals, double estimate_point, double h){
    double y_n = initial_vals.second;
    double k1 = 0;
    double k2 = 0;
    double y_n1 = 0;
    double x_n1 = initial_vals.first + h;

    while (x_n1 <= estimate_point){
         k1 = eval_function(initial_vals.first, y_n);
         k2 = eval_function(x_n1, y_n + (h*k1));
         y_n1 = y_n + h*((k1+k2)/2);
         initial_vals.first += h;
         x_n1 += h;
         y_n = y_n1;
}

    return y_n;
}

/*double h_approx_order_2(std::pair<double, double> initial_vals, double init_x2, double init_y2, double estimate_point, double h){
    double y_n1 = 0;
    double p_n1 = 0;
    double t = 0;

    while (t <= estimate_point){
        y_n1 = (1-(h*h)/2)*init_y1 + h*init_y2;
        p_n1 = -h*init_y1 + (1-(h*h)/2)*init_y2;
        init_y1 = y_n1;
        init_y2 = p_n1;
        t+= h;

    }
    return y_n1;
}
*/





int main(){
    std::string function = "";
    std::pair<double, double> initial_vals;
    double h = 0;
    double eval_point = 0;
    std::cout << "dy/dx = ";
    std::cin >> function;
    std::cout << "input your initial x";
    std::cin >> initial_vals.first;
    std::cout << "input your initial y";
    std::cin >> initial_vals.second;
    std::cout << "input step size";
    std::cin >> h;
    std::cout << "input what x value you want to estimate";
    std::cin >> eval_point;

    

    seprable_input(function);
    std::cout << h_approx_order_1(initial_vals,eval_point,h);


    return 0;
}