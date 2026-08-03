#include "parsing.hpp"
#include "exprtk.hpp"

    static double x;
    static double y;
    static exprtk::symbol_table<double> symbol_table;
    static exprtk::expression<double> expression;
void seprable_input(const std::string &function){
    symbol_table.add_variable("x", x);
    symbol_table.add_variable("y", y);
    symbol_table.add_constants();
    
    expression.register_symbol_table(symbol_table);

    exprtk::parser<double> parser;
    
    if (!parser.compile(function, expression)){
        std::cerr << "parse error\n";
        
    }
}

double eval_function(double x_val, double y_val){
    x = x_val;
    y = y_val;
    return expression.value();
}


static constexpr int MAX_ORDER = 10;
static double nth_x;
static double nth_z[MAX_ORDER];
static int current_order = 0;
static exprtk::symbol_table<double> nth_symbol_table;
static exprtk::expression<double>   nth_expression;

void nth_order_input(const std::string& function, int order) {
    current_order = order;
    nth_symbol_table.add_variable("x", nth_x);
    for (int i = 0; i < order; ++i) {
        nth_symbol_table.add_variable("y" + std::to_string(i), nth_z[i]);
    }
    nth_symbol_table.add_constants();
    nth_expression.register_symbol_table(nth_symbol_table);

    exprtk::parser<double> parser;
    if (!parser.compile(function, nth_expression)) {
        std::cerr << "nth order parse error\n";
    }
}

double eval_nth_order(double x_val, const std::vector<double>& z_vals) {
    nth_x = x_val;
    for (int i = 0; i < current_order; ++i) {
        nth_z[i] = z_vals[i];
    }
    return nth_expression.value();
}