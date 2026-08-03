#include "visualizer.hpp"
#include <mgl2/glut.h>
#include <mgl2/mgl.h>
#include <algorithm>
#include <cstdio>

namespace {

class Order1Plot : public mglDraw {
public:
    explicit Order1Plot(const std::vector<std::pair<double, double>>& trajectory) {
        long n = (long)trajectory.size();
        x.Create(n);
        y.Create(n);
        for (long i = 0; i < n; ++i) {
            x.a[i] = trajectory[i].first;
            y.a[i] = trajectory[i].second;
        }
    }

    int Draw(mglGraph* gr) override {
        gr->Title("ODE Solution");
        gr->SetRanges(x, y);
        gr->Adjust();
        gr->Axis();
        gr->Box();
        gr->Label('x', "x", 0);
        gr->Label('y', "y", 0);
        gr->Plot(x, y, "b2");
        return 0;
    }

private:
    mglData x, y;
};

class OrderNPlot : public mglDraw {
public:
    OrderNPlot(const std::vector<std::vector<double>>& trajectory, int order) : order(order) {
        long n = (long)trajectory.size();
        x.Create(n);
        ys.resize(order);
        for (auto& col : ys) col.Create(n);
        for (long i = 0; i < n; ++i) {
            x.a[i] = trajectory[i][0];
            for (int k = 0; k < order; ++k) ys[k].a[i] = trajectory[i][k + 1];
        }
    }

    int Draw(mglGraph* gr) override {
        static const char pens[] = "brgmck";
        const int npens = 6;

        mreal ymin = ys[0].Minimal(), ymax = ys[0].Maximal();
        for (int k = 1; k < order; ++k) {
            ymin = std::min(ymin, ys[k].Minimal());
            ymax = std::max(ymax, ys[k].Maximal());
        }

        gr->Title("ODE Solution");
        gr->SetRanges(x.Minimal(), x.Maximal(), ymin, ymax);
        gr->Adjust();
        gr->Axis();
        gr->Box();
        gr->Label('x', "x", 0);

        for (int k = 0; k < order; ++k) {
            char pen[8];
            std::snprintf(pen, sizeof(pen), "%c2", pens[k % npens]);
            gr->Plot(x, ys[k], pen);

            char legend[16];
            if (k == 0) std::snprintf(legend, sizeof(legend), "y");
            else std::snprintf(legend, sizeof(legend), "y^(%d)", k);
            gr->AddLegend(legend, pen);
        }
        gr->Legend();
        return 0;
    }

private:
    int order;
    mglData x;
    std::vector<mglData> ys;
};

}  // namespace

void show_order1(const std::vector<std::pair<double, double>>& trajectory) {
    Order1Plot plot(trajectory);
    mglGLUT gr(&plot, "ODE Solution Visualizer");
}

void show_order_n(const std::vector<std::vector<double>>& trajectory, int order) {
    OrderNPlot plot(trajectory, order);
    mglGLUT gr(&plot, "ODE Solution Visualizer");
}
