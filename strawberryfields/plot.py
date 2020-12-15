# Copyright 2018-2020 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""
This module provides tools to visualize the state in various interactive
ways using Plot.ly
"""
from copy import copy, deepcopy
import numpy as np

plotly_error = (
    "Plot.ly required for using this function. It can be installed using pip install "
    "plotly or visiting https://plot.ly/python/getting-started/#installation"
)


def _get_plotly():
    """Import Plot.ly on demand to avoid errors being raised unnecessarily"""
    try:
        # pylint:disable=import-outside-toplevel
        import plotly.io as pio
    except ImportError as e:
        raise (plotly_error) from e
    return pio

import numpy as np

textcolor = '#787878'

# Plot.ly default barchart JSON
barchartDefault = {
    'data': [{
        'y': [],
        'x': [],
        'type': "bar",
        'name': "q[0]"
    }],
    'layout': {
        'width': 835,
        'height': 500,
        'margin': {
            'l': 100,
            'r': 100,
            'b': 100,
            't': 100,
            'pad': 4
        },
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'autosize': True,
        'yaxis': {
            'gridcolor': "#bbb",
            'type': "linear",
            'autorange': True,
            'title': "Probability",
            'fixedrange': True
        },
        'xaxis': {
            'gridcolor': textcolor,
            'type': "category",
            'autorange': True,
            'title': "q[0]",
            'fixedrange': True
        },
        'showlegend': False,
        'annotations': [{
            "showarrow": False,
            "yanchor": "bottom",
            "xref": "paper",
            "xanchor": "center",
            "yref": "paper",
            "text": "",
            "y": 1,
            "x": 0,
            "font": {
                    "size": 16
            }
        }]
    },
    'config': {
        'modeBarButtonsToRemove': ['zoom2d','lasso2d','select2d','toggleSpikelines'],
        'displaylogo': False
    }
}

def plot_wigner(state, mode, xvec, pvec, renderer="browser", contours=True):
    """Plot the Wigner function with Plot.ly.

    Args:
        state (:class:`.BaseState`): the state used for plotting
        mode (int): mode used to calculate the reduced Wigner function
        xvec (array): array of discretized :math:`x` quadrature values
        pvec (array): array of discretized :math:`p` quadrature values
        renderer (string): the renderer for plotting with Plot.ly
        contours (bool): whether to show the contour lines in the plot
    """
    pio = _get_plotly()
    pio.renderers.default = renderer

    data = state.wigner(mode, xvec, pvec)
    new_chart = generate_wigner_chart(data, xvec, pvec, contours=contours)
    pio.show(new_chart)


def generate_wigner_chart(data, xvec, pvec, contours=True):
    """Populates a chart dictionary with reduced Wigner function surface plot data.

    Args:
        data (array): 2D array of size [len(xvec), len(pvec)], containing reduced
            Wigner function values for specified x and p values.
        xvec (array): array of discretized :math:`x` quadrature values
        pvec (array): array of discretized :math:`p` quadrature values
        contours (bool): whether to show the contour lines in the plot

    Returns:
        dict: a Plot.ly JSON-format surface plot
    """
    textcolor = "#787878"

    chart = {
        "data": [
            {
                "type": "surface",
                "colorscale": [],
                "x": [],
                "y": [],
                "z": [],
                "contours": {
                    "z": {},
                },
            }
        ],
        "layout": {
            "scene": {
                "xaxis": {},
                "yaxis": {},
                "zaxis": {},
            }
        },
    }

    chart["data"][0]["type"] = "surface"
    chart["data"][0]["colorscale"] = [
        [0.0, "purple"],
        [0.25, "red"],
        [0.5, "yellow"],
        [0.75, "green"],
        [1.0, "blue"],
    ]

    chart["data"][0]["x"] = xvec.tolist()
    chart["data"][0]["y"] = pvec.tolist()
    chart["data"][0]["z"] = data.tolist()

    chart["data"][0]["contours"]["z"]["show"] = contours

    chart["data"][0]["cmin"] = -1 / np.pi
    chart["data"][0]["cmax"] = 1 / np.pi

    chart["layout"]["paper_bgcolor"] = "white"
    chart["layout"]["plot_bgcolor"] = "white"
    chart["layout"]["font"] = {"color": textcolor}
    chart["layout"]["scene"]["bgcolor"] = "white"

    chart["layout"]["scene"]["xaxis"]["title"] = "x"
    chart["layout"]["scene"]["xaxis"]["color"] = textcolor
    chart["layout"]["scene"]["yaxis"]["title"] = "p"
    chart["layout"]["scene"]["yaxis"]["color"] = textcolor
    chart["layout"]["scene"]["yaxis"]["gridcolor"] = textcolor
    chart["layout"]["scene"]["zaxis"]["title"] = "W(x,p)"

    return chart

def plot_fock(state, modes, cutoff=None, renderer="browser"):
    """Plot the Fock state probabilities with Plot.ly.

    Args:
        state (:class:`.BaseState`): the state used for plotting
        modes (list): list of modes to generate output for
        cutoff (int): the cutoff value determining the maximum Fock state to
            get probabilities for
        xvec (array): array of discretized :math:`x` quadrature values
        pvec (array): array of discretized :math:`p` quadrature values
        renderer (string): the renderer for plotting with Plot.ly
        contours (bool): whether to show the contour lines in the plot
    """
    if cutoff is None:
        cutoff = state.cutoff_dim

    pio = _get_plotly()
    pio.renderers.default = renderer

    num_modes= len(modes)

    # Reduced density matrices
    rho = [state.reduced_dm(n, cutoff=cutoff) for n in range(num_modes)]
    print(rho)
    photonDists = np.array([np.real(np.diagonal(p)) for p in rho])

    n = np.arange(cutoff)
    print(photonDists)
    mean = [np.sum(n*probs).real for probs in photonDists]

    xlabels = ["|{}>".format(i) for i in range(0, cutoff, 1)]

    basic_chart = deepcopy(barchartDefault)
    new_chart = generate_fock_chart(basic_chart, modes, photonDists, mean, xlabels)
    pio.show(new_chart)

def generate_fock_chart(chart, modes, photonDists, mean, xlabels):
    """Populates a chart dictionary with marginal Fock state probability
    distributions.

    Args:
        chart (dict): chart dictionary to be used for plotting
        modes (list): list of modes to generate Fock charts for
        photonDists (list): nested list containing marginal Fock probabilities
            for each mode.
        mean (list): mean photon number for each mode
        xlabels (list): x-axis tick labels
    Returns:
        dict: a Plot.ly JSON-format bar chart
    """
    numplots = len(modes)
    chart['data'] = [dict() for i in range(numplots)]

    for idx, n in enumerate(sorted(modes)):
        chart['data'][idx]['type'] = 'bar'
        chart['data'][idx]['marker'] = {'color': '#1f9094'}
        chart['data'][idx]['x'] = xlabels
        chart['data'][idx]['y'] = photonDists[n].tolist()

        if idx == 0:
            Xax = ("xaxis", "x")
        else:
            chart['layout']['annotations'].append(copy(chart['layout']['annotations'][idx - 1]))
            Xax = ("xaxis{}".format(idx + 1), "x{}".format(idx + 1))

        chart['data'][idx]['xaxis'] = Xax[1]
        chart['data'][idx]['yaxis'] = 'y'
        chart['data'][idx]['name'] = ""

        dXa = 0.01 if idx != 0 else 0
        dXb = 0.01 if idx != numplots - 1 else 0

        chart['layout'][Xax[0]] = {
            'type': 'category',
            'domain': [idx / numplots + dXa, (idx + 1) / numplots - dXb],
            'title': "mode {}".format(n),
            'fixedrange': True,
            'gridcolor': 'rgba(0,0,0,0)'
        }

        chart['layout']['annotations'][idx]["text"] = "Mean: {:.3f}".format(mean[n])
        chart['layout']['annotations'][idx]["x"] = idx / numplots + dXa +0.5/numplots

    chart['layout']['xaxis']['type'] = 'category'
    chart['layout']['title'] = 'Marginal Fock state probabilities'

    chart['layout']['font'] = {'color': textcolor}
    chart['layout']['font'] = {'color': textcolor}

    return chart