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