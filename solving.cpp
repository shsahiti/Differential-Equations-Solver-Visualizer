#include "solving.hpp"


double h_approx_order_1(std::pair<double, double> initial_vals, double estimate_point, double h){
    double y_n = initial_vals.second;
    double k1 = 0;
    double k2 = 0;
    double k3 = 0;
    double k4 = 0;
    double y_n1 = 0;
    double x_n1 = initial_vals.first;

     while (x_n1 <= estimate_point) {
         k1 = eval_function(x_n1, y_n);
         k2 = eval_function(x_n1 + h/2 , y_n + (h/2)*k1);
         k3 = eval_function(x_n1 + h/2 , y_n + (h/2)*k2);
         k4 = eval_function(x_n1 + h, y_n1 + h*k3);
         y_n1 = y_n + (h/6)*(k1 + 2*k2 + 2*k3 + k4);
         x_n1 += h;
         y_n = y_n1;
}
return y_n;
}





