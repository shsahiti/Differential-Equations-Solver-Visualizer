#include "solving.hpp"
#include "parsing.hpp"
#include "visualizer.hpp"
#include <iomanip>
#include <fstream>

static void write_order1_csv(const std::string& path, const std::vector<std::pair<double, double>>& trajectory) {
    std::ofstream out(path);
    out << "x,y\n";
    out << std::setprecision(15);
    for (const auto& point : trajectory) {
        out << point.first << "," << point.second << "\n";
    }
}

static void write_order_n_csv(const std::string& path, const std::vector<std::vector<double>>& trajectory, int order) {
    std::ofstream out(path);
    out << "x,y";
    for (int i = 1; i < order; ++i) out << ",y" << i;
    out << "\n";
    out << std::setprecision(15);
    for (const auto& row : trajectory) {
        for (size_t i = 0; i < row.size(); ++i) {
            if (i) out << ",";
            out << row[i];
        }
        out << "\n";
    }
}

int main(){
    int order = 0;
    std::cout << "ODE order: ";
    std::cin >> order;
    std::cin.ignore(); 

    std::string function = "";
    double h = 0;
    double eval_point = 0;

    if (order == 1) {
        std::pair<double, double> initial_vals;
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
        auto trajectory = h_approx_order_1(initial_vals, eval_point, h);

        std::cout << std::setprecision(15) << trajectory.back().second << "\n";
        write_order1_csv("trajectory.csv", trajectory);
        std::cout << "Trajectory written to trajectory.csv (" << trajectory.size() << " points)\n";
        show_order1(trajectory);
    } else {
        std::cout << "Enter y^(" << order << ") as f(x, y0, y1, ..., y" << order - 1 << ")\n";
        std::cout << "  (y0 = y, y1 = y', y2 = y'', ...)\n";
        std::cout << "f = ";
        std::getline(std::cin, function);

        double x0;
        std::cout << "initial x = ";
        std::cin >> x0;

        std::vector<double> z0(order);
        for (int i = 0; i < order; ++i) {
            std::cout << "y^(" << i << ")(" << x0 << ") = ";
            std::cin >> z0[i];
        }

        std::cout << "step = ";
        std::cin >> h;
        std::cout << "input what x value you want to estimate = ";
        std::cin >> eval_point;

        nth_order_input(function, order);
        auto trajectory = h_approx_order_n(x0, z0, eval_point, h);
        const auto& result = trajectory.back();

        std::cout << std::setprecision(15);
        std::cout << "y(" << eval_point << ") = " << result[1] << "\n";
        for (int i = 1; i < order; ++i) {
            std::cout << "y^(" << i << ")(" << eval_point << ") = " << result[i + 1] << "\n";
        }

        write_order_n_csv("trajectory.csv", trajectory, order);
        std::cout << "Trajectory written to trajectory.csv (" << trajectory.size() << " points)\n";
        show_order_n(trajectory, order);
    }

    return 0;
}
