#include "solving.hpp"
#include <functional>


std::vector<std::pair<double, double>> h_approx_order_1(std::pair<double, double> initial_vals, double estimate_point, double h){
    double y_n = initial_vals.second;
    double k1 = 0;
    double k2 = 0;
    double k3 = 0;
    double k4 = 0;
    double y_n1 = 0;
    double x_n1 = initial_vals.first;

    std::vector<std::pair<double, double>> trajectory;
    trajectory.push_back({x_n1, y_n});

     while (x_n1 < estimate_point - 1e-10) {
         k1 = eval_function(x_n1, y_n);
         k2 = eval_function(x_n1 + h/2.0 , y_n + (h/2.0)*k1);
         k3 = eval_function(x_n1 + h/2.0 , y_n + (h/2.0)*k2);
         k4 = eval_function(x_n1 + h, y_n + h*k3);
         y_n1 = y_n + (h/6.0)*(k1 + 2.0*k2 + 2.0*k3 + k4);
         x_n1 += h;
         y_n = y_n1;
         trajectory.push_back({x_n1, y_n});
}
return trajectory;
}

std::vector<std::vector<double>> h_approx_order_n(double x0, std::vector<double> initial_z, double estimate_point, double step) {
    int n = (int)initial_z.size();
    std::vector<double> z = initial_z;
    double x = x0;
    double h = step;

    auto derivatives = [&](double xv, const std::vector<double>& zv) {
        std::vector<double> dz(n);
        for (int i = 0; i < n - 1; ++i) dz[i] = zv[i + 1];
        dz[n - 1] = eval_nth_order(xv, zv);
        return dz;
    };

    auto vec_add = [&](const std::vector<double>& a, double s, const std::vector<double>& b) {
        std::vector<double> result(n);
        for (int i = 0; i < n; ++i) result[i] = a[i] + s * b[i];
        return result;
    };

    auto make_row = [&](double xv, const std::vector<double>& zv) {
        std::vector<double> row;
        row.reserve(n + 1);
        row.push_back(xv);
        row.insert(row.end(), zv.begin(), zv.end());
        return row;
    };

    std::vector<std::vector<double>> trajectory;
    trajectory.push_back(make_row(x, z));

    while (x < estimate_point - 1e-10) {
        auto k1 = derivatives(x,         z);
        auto k2 = derivatives(x + h/2.0, vec_add(z, h/2.0, k1));
        auto k3 = derivatives(x + h/2.0, vec_add(z, h/2.0, k2));
        auto k4 = derivatives(x + h,     vec_add(z, h,     k3));

        for (int i = 0; i < n; ++i) {
            z[i] = z[i] + (h / 6.0) * (k1[i] + 2.0*k2[i] + 2.0*k3[i] + k4[i]);
        }
        x += h;
        trajectory.push_back(make_row(x, z));
    }
    return trajectory;
}





