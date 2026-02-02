#include "headers.hpp"
#include <cmath>
#include <iostream>


double h_approx_order_1(double init_x, double init_y, double estimate_point, double step){
    double y_n = init_y;
    double k1 = 0;
    double k2 = 0;
    double y_n1 = 0;
    double x_n1 = init_x + step;

    while (x_n1 <= estimate_point){
         k1 = init_x*init_x + 2*y_n;
         k2 = (x_n1)*(x_n1) + 2*(y_n + (step*k1));
         y_n1 = y_n + step*((k1+k2)/2);
         init_x = init_x + step;
         x_n1 = x_n1 + step;
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
 std::cout << h_approx_order_2(0,1,2,0.5,2,0.5);
 return 0;
}