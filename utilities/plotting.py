import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
import os
import datetime

utils_dir = os.path.dirname(os.path.realpath(__file__))
plt.style.use('{}/kernel_pcovr.mplstyle'.format(utils_dir))


def plot_base(scatter_points, fig, ax, title, x_label, y_label, cbar=True,
              cbar_title="", cb_orientation='vertical', cb_ax = None, rasterized=True,
              **kwargs):
    """
        Base class for all plotting utilities
        Author: Rose K. Cersonsky

        ---Variables---
        scatter_points: (array) n-dimensional data to plot
                        first two components are plotted
        fig, ax: figure and axis to plot on, as generated by plt.subplots()
        title: (str) title for plot
        x_label, y_label: (str) labels for x-axis and y-axis
        cbar_title: (str) label for colorbar
        kwargs: arguments to pass to plt.scatter

    """

    # print(kwargs)
    if(ax is None or fig is None):
        fig, ax = plt.subplots(1, figsize=plt.rcParams['figure.figsize'])

    cb_args = kwargs.get('cb_args', {})
    if('cb_args' in kwargs):
        kwargs.pop('cb_args')

    p = ax.scatter(scatter_points[:, 0],
                   scatter_points[:, 1],
                   rasterized=rasterized,
                   **kwargs
                   )

    if('cmap' in kwargs and cbar==True):

        if(cb_ax is None):
            cb_args['ax'] = ax
            cb_args['fraction'] = cb_args.get('fraction', 0.4)
        else:
            cb_args['cax'] = cb_ax
            cb_args['fraction'] = cb_args.get('fraction', 1.0)

        cbar = fig.colorbar(p, **cb_args,
                            orientation=cb_orientation,
                            )

        if(cb_orientation=='horizontal'):
            cbar.ax.set_xlabel(cbar_title)
        else:
            cbar.ax.set_ylabel(cbar_title)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    return fig, ax


def plot_simple(X, fig=None, ax=None, title=None, labels=[r"$X_1$", r"$X_2$"], **kwargs):
    """
        Create simple plot of 2+ dimensional data
        Author: Rose K. Cersonsky

        ---Variables---
        X: (array) n-dimensional data to plot
                        first two components will be plotted
        fig, ax: figure and axis to plot on, as generated by plt.subplots()
        title: (str) title for plot
        labels: (str) labels for x-axis and y-axis
        kwargs: arguments to pass to plt.scatter
    """

    if('cmapY' in kwargs):
        kwargs.pop('cmapY')
    if('cmapX' in kwargs):
        kwargs.pop('cmapX')
    if('color' not in kwargs):
        kwargs['color'] = 'b'

    fig, ax = plot_base(scatter_points=X, fig=fig, ax=ax, title=title,
                        alpha=1.0,
                        x_label=labels[0],
                        y_label=labels[1],
                        **kwargs
                        )
    return ax


def plot_projection(Y, T, fig=None, ax=None, Y_scale=1.0, Y_center=0.0, **kwargs):
    """
        Create a plot of a latent-space projection of data
        Author: Rose K. Cersonsky

        ---Variables---
        Y: (array) property to use for the colorbar
        T: (array) latent-space projection
        fig, ax: figure and axis to plot on, as generated by plt.subplots()
        kwargs: arguments to pass to plt.scatter,
                may contain cbar_title, x_label, y_label, and title
                    for non-typical plots
    """

    Y = Y.reshape(Y.shape[0], -1)
    if(len(T.shape)==1 or T.shape[-1]==1):
        T = np.array([T[:,0], np.zeros(T.shape[0])]).T

    if('color' not in kwargs):
        if Y.shape[-1] != 1:
            if('cmap2D' in kwargs and 'colormap' not in kwargs):
                if('vmin' not in kwargs or 'vmax' not in kwargs):
                    bounds = np.array([np.mean(Y, axis=0)-np.std(Y, axis=0),
                                       np.mean(Y, axis=0)+np.std(Y, axis=0)]).T
                else:
                    bounds = np.array([kwargs['vmin'], kwargs['vmax']]).T
                    kwargs.pop('vmin'); kwargs.pop('vmax');

                bounds = bounds[:2]
                colormap = kwargs['cmap2D'](*bounds)
                kwargs['c'] = [colormap(y) for y in Y]
            elif('colormap' in kwargs):
                kwargs['c'] = [kwargs['colormap'](y) for y in Y]
                kwargs.pop('colormap')
            else:
                Y = Y[:, 0]
                if isinstance(Y_scale, np.ndarray) or isinstance(Y_scale, list):
                    Y_scale = Y_scale[0]
                if isinstance(Y_center, np.ndarray) or isinstance(Y_center, list):
                    Y_center = Y_center[0]
                kwargs['c'] = Y * Y_scale + Y_center
            if('cmap' in kwargs):
                kwargs.pop('cmap')
            if('vmin' in kwargs):
                kwargs.pop('vmin'); kwargs.pop('vmax')
        elif('c' not in kwargs):
            Y = Y[:, 0]
            Y_center = np.array([Y_center])
            Y_center = Y_center.reshape(Y_center.shape[0], -1)
            Y_center = Y_center[0]

            if('colormap' in kwargs):
                kwargs['c'] = [kwargs['colormap']( (y-min(Y)) / (max(Y) - min(Y))) for y in Y]
                kwargs.pop('colormap')
            else:
                kwargs['c'] = Y * Y_scale + Y_center
                kwargs['cmap'] = kwargs.get('cmapX', "viridis")

        if('cmap2D' in kwargs):
            kwargs.pop('cmap2D')
        if('colormap' in kwargs):
            kwargs.pop('colormap')

    if('cmapY' in kwargs):
        kwargs.pop('cmapY')
    if('cmapX' in kwargs):
        kwargs.pop('cmapX')

    kwargs['cbar_title'] = kwargs.get('cbar_title', "CS")
    kwargs['x_label'] = kwargs.get('x_label', r'$PC_1$')
    kwargs['y_label'] = kwargs.get('y_label', r'$PC_2$')
    kwargs['title'] = kwargs.get('title', None)

    fig, ax = plot_base(scatter_points=T, fig=fig, ax=ax, **kwargs)
    return ax


def plot_regression(Y, Yp, fig=None, ax=None, Y_scale=1.0, Y_center=0.0, **kwargs):
    """
        Create a plot of a regressed data
        Author: Rose K. Cersonsky

        ---Variables---
        Y: (array) property to compare against
        Yp: (array) predicted property
        fig, ax: figure and axis to plot on, as generated by plt.subplots()
        kwargs: arguments to pass to plt.scatter,
                may contain cbar_title, x_label, y_label, and title
                    for non-typical plots
    """
    if len(Y.shape) != 1:
        print("Only plotting first column of Y")
        Y = Y[:, 0]
        Yp = Yp[:, 0]
        if isinstance(Y_scale, np.ndarray) or isinstance(Y_scale, list):
            Y_scale = Y_scale[0]
        if isinstance(Y_center, np.ndarray) or isinstance(Y_center, list):
            Y_center = Y_center[0]
    kwargs['cmap'] = kwargs.get('cmapY', 'Greys')

    if('cmapY' in kwargs):
        kwargs.pop('cmapY')
    if('cmapX' in kwargs):
        kwargs.pop('cmapX')
    if('cmap2D' in kwargs):
        kwargs.pop('cmap2D')

    if('color' not in kwargs):
        kwargs['c'] = Y_scale * np.abs(Y - Yp)

    kwargs['cbar_title'] = kwargs.get('cbar_title', "Loss")
    kwargs['x_label'] = kwargs.get('x_label', r'$Y$')
    kwargs['y_label'] = kwargs.get('y_label', r'$Xw$')
    kwargs['title'] = kwargs.get('title', None)

    plot_points = np.add(np.multiply(Y_scale, [Y, Yp]), Y_center)

    fig, ax = plot_base(scatter_points=plot_points.T, fig=fig, ax=ax, **kwargs)

    cm = np.mean(plot_points, axis=1)
    bound = max(np.abs(plot_points[0]-cm[0]).max(),
                np.abs(plot_points[1]-cm[1]).max())
    ax.set_xlim([cm[0]-bound, cm[0]+bound])
    ax.set_ylim([cm[1]-bound, cm[1]+bound])
    ax.plot([cm[0]-bound, cm[0]+bound], [cm[1]-bound,
                                         cm[1]+bound],
            'r--', zorder=4, linewidth=1)

    return ax


def get_cmaps():
    from .colorbars import load

    load()

    return dict(
        cmapY='Greys',
        cmapX='cbarHot',
        edgecolor='k'
    )


def markdown_table(data, headers, columns, title, precision=1e-3):

    return display(Markdown(f'<center><b> {title} </b></center><br>\
                            <center><table><tr><th></th><th><center>' +
                            '</center></th><th><center>'.join(headers) +
                            '</center></th></tr>' +
                            '</tr><tr>'.join([f'<td> {c} </td>\
                                                <td> {" </td><td> ".join([dd for dd in d])} </td>' for c, d in zip(columns, data)]) +
                            "</tr></table></center>"))


def table_from_dict(dictionaries, headers, title='', precision=1e-6):
    columns = []
    for d in dictionaries:
        for k in d:
            if k not in columns:
                columns.append(k)
    data = [["{:g}".format(d[k]) if k in d else '' for d in dictionaries]
            for k in columns]
    return markdown_table(data, headers, columns, title, precision=precision)


def check_mirrors(X1, X2):
    # Checking if the PCs of the sparse kernel are reflections of those for the full kernel
    def hist_dist(x, xr):
        hp, bp = np.histogramdd(x, bins=20, normed=True)
        hq, bq = np.histogramdd(xr, bins=20, normed=True)
        return np.linalg.norm(hp-hq)

    X = X1.copy()
    Xref = X2.copy()

    X = np.subtract(X, np.mean(X, axis=0))
    Xref = np.subtract(Xref, np.mean(Xref, axis=0))

    Xscale = np.linalg.norm(X)
    X = X / Xscale
    Xref = Xref / np.linalg.norm(Xref)

    if(hist_dist(X[:, 0], Xref[:, 0]) > hist_dist(-X[:, 0], Xref[:, 0])):
        xflip = -1
    else:
        xflip = 1
    if(hist_dist(X[:, 1], Xref[:, 1]) > hist_dist(-X[:, 1], Xref[:, 1])):
        yflip = -1
    else:
        yflip = 1

    return (xflip, yflip)*X1[:, :2]
