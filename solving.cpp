#include "solving.hpp"
#include <cmath>
#include <iostream>
#include "parsing.hpp"


double h_approx_order_1(double init_x, double init_y, double estimate_point, double h, ){
    double y_n = init_y;
    double k1 = 0;
    double k2 = 0;
    double y_n1 = 0;
    double x_n1 = init_x + h;

    while (x_n1 <= estimate_point){
         k1 = f(init_x, y_n);
         k2 = f(x_n1, y_n + (h*k1))
         y_n1 = y_n + h*((k1+k2)/2);
         init_x = init_x + h;
         x_n1 = x_n1 + h;
         y_n = y_n1;
}

    return y_n;
}

double h_approx_order_2(double init_x1, double init_y1, double init_x2, double init_y2, double estimate_point, double h){
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





int main(){
    std::string function = "";
    std::pair
    std::cout << "dy/dx = ";
    std::cin >> function;
    std::cout << "input your initial x";
    std::cin >> init_x1;
    std::cout << "input your initial y";
    

    seprable_input(function);
    h_approx_order_1()


    return 0;
}