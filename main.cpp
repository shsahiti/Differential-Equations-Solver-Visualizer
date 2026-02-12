#include "solving.hpp"
#include "parsing.hpp"

int main(){
    std::string function = "";
    std::pair<double, double> initial_vals;
    double h = 0;
    double eval_point = 0;
    std::cout << "dy/dx = ";
    std::getline(std::cin, function);
    std::cout << "initial x = ";
    std::cin >> initial_vals.first;
    std::cout << "initial y = ";
    std::cin >> initial_vals.second;
    std::cout << "step = ";
    std::cin >> h;
    std::cout << "input what x value you want to estimate = ";
    std::cin >> eval_point;

    

    seprable_input(function);
    std::cout << h_approx_order_1(initial_vals,eval_point,h);
    


    return 0;
}