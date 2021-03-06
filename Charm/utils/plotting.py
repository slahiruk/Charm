# matplotlib.use('Agg')

import itertools
import logging

# from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl
import numpy as np
from matplotlib import cm as cm
from matplotlib import pyplot as plt


class PlotHelper(object):

    @staticmethod
    def plot_3d_surface(X, Y, Z, title=None):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.set_xlabel(r'$\sigma_1$', fontsize=20)
        ax.set_ylabel(r'$\sigma_2$', fontsize=20)
        ax.set_ylim([-0.1, 1.1])
        ax.set_xlim([-0.1, 1.1])
        ax.set_xticks([.0, .2, .4, .6, .8, 1.])
        ax.set_yticks([.0, .2, .4, .6, .8, 1.])
        X, Y = np.meshgrid(X, Y)
        logging.debug('X: {}\nY:{}\nZ:{}'.format(X, Y, Z))
        surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                linewidth=0, antialiased=True)
        ax.view_init(90, 90)
        #fig.colorbar(surf, shrink=.5, aspect=5)
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()

    @staticmethod
    def plot_3d_surfaces(Xs, Ys, Zs, labels, title=None):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        for t in ax.zaxis.get_major_ticks():
            t.label.set_fontsize(10)
        for t in ax.xaxis.get_major_ticks():
            t.label.set_fontsize(10)
        for t in ax.yaxis.get_major_ticks():
            t.label.set_fontsize(10)
        ax.set_xlabel(r'$\sigma_1$', fontsize=20)
        ax.set_ylabel(r'$\sigma_2$', fontsize=20)
        ax.set_zlabel(r'$Normalized Performance$', fontsize=10)
        ax.set_ylim([-0.1, 1.1])
        ax.set_xlim([-0.1, 1.1])
        #ax.set_zlim([0.9, 1.1])
        ax.set_xticks([.0, .2, .4, .6, .8, 1.])
        ax.set_yticks([.0, .2, .4, .6, .8, 1.])
        #ax.set_zticks([.9, .95, 1, 1.05, 1.1])
        colors = itertools.cycle(('black', 'blue'))
        fake_lines = []
        for X, Y, Z in zip(Xs, Ys, Zs):
            X, Y = np.meshgrid(X, Y)
            color = next(colors)
            surf = ax.plot_surface(X, Y, Z, color=color, alpha=.6,
                    linewidth=0, antialiased=True)
            fake_lines.append(mpl.lines.Line2D([0],[0], linestyle='none', c=color, marker='o'))
        ax.legend(fake_lines, labels)
        ax.view_init(30, 120)
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()

    @staticmethod
    def plot_hists(d2perf, sort_func, col=None, title=None):
        """ Plot a series of histograms in one figure.

        Args:
            d2perf: design point to perf distribution, d -> [perf]
        """
        bins = 30
        sorted_perf = sorted(iter(d2perf.items()), key=sort_func, reverse=False)
        x, labels = [], []
        for d, perf in sorted_perf:
            x.append(perf)
            labels.append(str(d))
        colors = cm.rainbow(np.linspace(0, 1, len(x)))
        plt.figure(1)
        total_plots = len(x)
        for i in range(total_plots):
            if not col:
                plt.subplot(int(total_plots/np.sqrt(total_plots)) + 1, int(np.sqrt(total_plots)), i+1)
            else:
                plt.subplot(total_plots/col, col, i+1)
            plt.hist(x[i], bins, alpha=.5, normed=True,
                    label="mean: {}".format(np.mean(x[i])), color=colors[i])
            plt.legend(loc='upper right', fancybox=True, shadow=True, fontsize=4)
            plt.xticks([])
            plt.yticks([])

        if title:
            plt.savefig(title + '.png', bbox_inches='tight')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_core_area_dist(xs, color=None, title=None):
        plt.yticks([])
        plt.ylim([0, 256])
        index = np.arange(len(xs))
        plt.bar(index, xs, color=color if color else 'blue')
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_core_dist(xs, color=None, title=None):
        plt.yticks([])
        #plt.ylim([0, 16])
        plt.xlim([1, 7])
        plt.xticks([1.5, 2.5, 3.5, 4.5, 5.5, 6.5], ['8', '16', '32', '64', '128', '256'])
        plt.hist(xs, bins = [0, 1, 2, 3, 4, 5, 6], alpha=.3, color = color if color else 'blue')
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_hist(xs, color=None, title=None):
        bins=50
        plt.yticks([])
        #plt.xticks([0, .2, .4, .6, .8, 1., 2., 3., 4.], 
        #        ['0', '0.2', '0.4', '0.6', '0.8', '1.0', '2.0', '3.0', '4.0'], rotation=60)
        #plt.xlabel('Normalized Performance', fontsize=20)
        #plt.xlim([0, 4])
        plt.hist(xs, bins = bins, alpha=.3, color = color if color else 'black')
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_overlap_hists(list_of_xs, title=None):
        bins = 50
        colors = itertools.cycle(('black', 'blue', 'red'))
        plt.yticks([])
        for xs in list_of_xs:
            plt.hist(xs, bins=bins, alpha=.3, color=next(colors), normed=1)
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_perf_hist(perf, title=None):
        """ Plot a single histogram.

        Args:
            perf: list of performance numbers
        """
        bins = 50
        plt.hist(perf, bins, alpha=.3, normed=0)
        plt.xlabel('Normalized Performance', fontsize=20)
        plt.ylabel('Count', fontsize=20)
        plt.xlim(xmin=0)
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_scatter(s2pl, scatter=None, top=None, annotate=False, title=None):
        """ Plot a series of scatter points.

        Args:
            s2points: series of points.
        """
        num_series = len(list(s2pl.keys()))
        colors = cm.rainbow(np.linspace(0, 1, num_series))
        marker = itertools.cycle(('o' , 'v', '^', '<', '>', 'D', 's', '*', 'x', '+', 'H'))

        for series, points, c in zip(list(s2pl.keys())[:top], list(s2pl.values())[:top], colors):
            x = [point.perf for point in points]
            y = [point.risk for point in points]
            designs = [point.design for point in points]
            legend = '(' + str(series[0])[:3] + ',' + str(series[1])[:3] + ')'
            plt.plot(x, y, color=cm.Greys(series[0] + series[1]), marker=next(marker), alpha=.5, label=legend)
            if annotate:
                for i in range(len(designs)):
                    plt.annotate(designs[i], (x[i], y[i]), fontsize=8)
                    plt.annotate(series, (x[i], y[i] + .01), fontsize=8)
        if scatter:
            for series, points, c in zip(list(scatter.keys())[:top], list(scatter.values())[:top], colors):
                x = [point.perf for point in points]
                y = [point.risk for point in points]
                designs = [point.design for point in points]
                legend = '(' + str(series[0])[:3] + ',' + str(series[1])[:3] + ')'
                plt.scatter(x, y, color='black', marker='o', alpha=.5)

        plt.xlabel('Normalized Performance', fontsize=20)
        plt.ylabel('Normalized Risk', fontsize=20)
        #plt.xlim([0.8, 1.2])
        #plt.ylim([0, 1.1])
        plt.legend(loc='upper right', 
                fancybox=True, shadow=True, fontsize=12)
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()
        plt.clf()    

    @staticmethod
    def plot_risk_perf_for_candidate(series, title=None):
        marker = itertools.cycle(('o-' , 'v-', '^-', '<-', '>-', 'D-', 's-', '*-', 'x-', '+-', 'H-'))
        for k, points in series.items():
            xs = [p[1] for p in points]
            ys = [p[2] for p in points]
            annos = [p[0] for p in points]
            plt.plot(xs, ys, next(marker), alpha=.6)
            for i in range(len(annos)):
                plt.annotate(annos[i], (xs[i], ys[i]), fontsize=8)
        #plt.xlim([0.8, 1.1])
        plt.xlabel('Normalized Performance', fontsize=18)
        plt.ylabel('Risk', fontsize=18)
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_shift_scatter(points, title=None):
        marker_size = 80

        optimal_marker = 'o'
        perf_optimal_marker = '^'
        risk_optimal_marker = 'v'
        sub_optimal_marker = 's'
        sub_optimal_tradeoff_marker = 'D'

        optimal_points = [p[0] for p in points if p[1] and p[2]]
        perf_optimal_points = [p[0] for p in points if p[1] and not p[2]]
        risk_optimal_points = [p[0] for p in points if not p[1] and p[2]]
        sub_optimal_points = [p[0] for p in points if not p[1] and not p[2] and p[3]]
        sub_optimal_tradeoff_points = [p[0] for p in points if not p[1] and not p[2] and not p[3]]
        plt.scatter([p[0] for p in optimal_points], [p[1] for p in optimal_points],
                marker=optimal_marker, s=marker_size)
        plt.scatter([p[0] for p in perf_optimal_points], [p[1] for p in perf_optimal_points],
                marker=perf_optimal_marker, s=marker_size)
        plt.scatter([p[0] for p in risk_optimal_points], [p[1] for p in risk_optimal_points],
                marker=risk_optimal_marker, s=marker_size)
        plt.scatter([p[0] for p in sub_optimal_points], [p[1] for p in sub_optimal_points],
                marker=sub_optimal_marker, s=marker_size)
        plt.scatter([p[0] for p in sub_optimal_tradeoff_points],
                [p[1] for p in sub_optimal_tradeoff_points],
                marker=sub_optimal_tradeoff_marker, s=marker_size)
        plt.xlabel(r'$\sigma_1$', fontsize=16)
        plt.ylabel(r'$\sigma_2$', fontsize=16)
        #plt.ylim([-0.1, 1.1])
        #plt.xlim([-0.1, 1.1])
        #plt.xticks([.0, .2, .4, .6, .8, 1.], ['0', '0.2', '0.4', '0.6', '0.8', '1.0'])
        #plt.yticks([.0, .2, .4, .6, .8, 1.], ['0', '0.2', '0.4', '0.6', '0.8', '1.0'])
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_shift_prob(points, title=None):
        plt.scatter([p[0][0] for p in points],
                [p[0][1] for p in points], c=[p[1] * 100 / 255 for p in points])
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_heatmap(data, title=None):
        plt.imshow(data, cmap='hot')
        if title:
            plt.savefig(title + '_perf.png')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_approx_curve(xs, list_perfs, list_risks, title=None):
        marker = itertools.cycle(('o-' , 'x-', '^-', '<-', 'H-'))
        perfs, risks = [], []
        for i in range(len(list_perfs[0])):
            perfs.append([])
            risks.append([])
        for ps, rs in zip(list_perfs, list_risks):
            print(ps)
            for index, val in enumerate(ps):
                print(perfs[index])
                perfs[index].append(val)
                print(perfs)
            for index, val in enumerate(rs):
                risks[index].append(val)
        plt.xticks(xs, [10000, 1000, 100, 50, 20])
        plt.xlabel(r'Sample size $k$', fontsize=20)
        plt.ylabel(r'Performance Deviation (%)', fontsize=20)
        plt.ylim([0, 0.2])
        
        for ps in perfs[2:]:
            plt.plot(xs, ps, next(marker))
        if title:
            plt.savefig(title + '_perf.png', bbox_inches='tight')
        else:
            plt.show()
        plt.clf()
        marker = itertools.cycle(('o-' , 'x-', '^-', '<-', 'H-'))
        plt.xticks(xs, [10000, 1000, 100, 50, 20])
        plt.xlabel(r'Sample size $k$', fontsize=20)
        plt.ylabel(r'Risk Deviation (%)', fontsize=20)
        plt.ylim([0, 0.2])
        for rs in risks[2:]:
            plt.plot(xs, rs, next(marker))
        if title:
            plt.savefig(title + '_risk.png', bbox_inches='tight')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_multiple_trends(list_x2y, legends, title=None):
        marker = itertools.cycle(('o' , 'v', '^', '<', '>', 'D', 's', '*', 'x', '+', 'H'))
        for i in range(len(list_x2y)):
            x2y = list_x2y[i]
            xs, ys = [], []
            for x, y in x2y.items():
                xs.append(x)
                ys.append(y)
            plt.plot(xs, ys, next(marker), label=legends[i])
        plt.legend(loc='upper left', fancybox=True, shadow=True, fontsize=12)
        plt.show()

    @staticmethod
    def plot_trend(x2y, title=None):
        """ Plot a trend curve of y vs. x.
        """
        xs, ys = [], []
        for x, y in x2y.items():
            xs.append(x)
            ys.append(y)
        plt.plot(xs, ys, 'o')
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_trends(legends, list_of_x2y, const_perf, std=False, title=None):
        assert(len(legends) == len(list_of_x2y))
        marker = itertools.cycle(('o-' , 'v-', '^-', '<-', '>-', 'D-', 's-', '*-', 'x-', '+-', 'H-'))
        lines = []
        for i in range(len(list_of_x2y)):
            xys = sorted([(k, v) for k, v in list_of_x2y[i].items()], key=lambda t: t[0])
            xs = [t[0] for t in xys]
            const_ys = [const_perf/const_perf] * (len(xs)+1)
            ys_45 = xs + [1.1]
            ys = [t[1][0]/const_perf for t in xys]
            yerrs = [t[1][1]/const_perf for t in xys]
            if not std:
                plt.ylim([.7, 1.3])
            else:
                plt.ylim([-0.05, 2])
            plt.xlim([0, 1.05])
            #lines.append(plt.scatter(xs, yerrs, marker=marker.next()))
            if not std:
                lines.append(plt.plot(xs, ys,
                                      next(marker), markersize=10, alpha=.6, label=legends[i]))
                plt.plot(xs+[1.1], const_ys, 'k--', alpha=.2)
            else:
                lines.append(plt.plot(xs, yerrs,
                                      next(marker), markersize=10, alpha=.6, label=legends[i]))
                plt.plot(xs+[1.1], ys_45, 'k--', alpha=.2)
        plt.xlabel(r'Input $\sigma$', fontsize=20)
        if not std:
            plt.ylabel(r'Normalized Performance', fontsize=20)
        else:
            plt.ylabel(r'Output $\sigma$', fontsize=20)
        #plt.legend(loc='upper center', ncol=3,
        #        bbox_to_anchor=(.5, 1.05), fancybox=True, shadow=True, fontsize=8)
        if title:
            if not std:
                plt.savefig(title + '_perf.png', bbox_inches='tight')
            else:
                plt.savefig(title + '_std.png', bbox_inches='tight')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_gp_regression(f, trans_func=None, x2y=None, samples=None, title=None):
        X = np.linspace(0, 6, 100)
        y_mean, y_cov = f(X[:, np.newaxis], return_cov = True)
        if trans_func:
            X = trans_func(X)
            y_mean = trans_func(y_mean)
            y_cov = trans_func(y_cov)
        y_mean = y_mean.reshape(y_mean.shape[0])
        plt.plot(X, y_mean, 'r')
        plt.fill_between(X, y_mean - np.sqrt(np.diag(y_cov)), y_mean + np.sqrt(np.diag(y_cov)),
                alpha=.5, color = 'k')
        if x2y is not None:
            xs, ys = [], []
            for x, y in x2y.items():
                xs.append(x)
                ys.append(y)
            plt.plot(xs, ys, 'o')
        if samples is not None:
            xs, ys = [], []
            for (x, y) in samples:
                xs.append(x)
                ys.append(y)
            plt.plot(xs, ys, 'x')
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def plot_KDE(xs, pdf, trans_func = None, ground_truth = None, resamples = None, title = None):
        bins = 20
        plt.yticks([])
        if trans_func is not None:
            plt.plot([trans_func(x) for x in xs], [trans_func(x) for x in pdf(xs)], 'r')
        else:
            plt.plot(xs, pdf(xs), 'r')
        if ground_truth is not None:
            plt.hist(ground_truth, bins = bins, normed=1, alpha=.3, color='black')
        if resamples is not None:
            #plt.plot(resamples, np.zeros_like(resamples), alpha=.5,
            #        marker='+', markersize=20, color='black')
            plt.hist(resamples, bins = bins, normed=1, alpha=.3, color='blue')
        if title:
            plt.savefig(title + '.png')
        else:
            plt.show()
        plt.clf()
