# Blender import system clutter
import sys
from pathlib import Path

UTILS_PATH = Path.home() / "Documents/python_workspace/data-science-learning"
SRC_PATH = UTILS_PATH / "graphics/morphogenesis"
sys.path.append(str(UTILS_PATH))
sys.path.append(str(SRC_PATH))

import Morphogenesis
import importlib
importlib.reload(Morphogenesis)
from Morphogenesis import Morphogenesis

import bpy
from math import cos, sin, pi
import numpy as np

from ds_utils.blender_utils import draw_line, draw_segment, get_grease_pencil, get_grease_pencil_layer


def run_morphogenesis(morphogenesis_config, gp_layer, nodes, is_circle, draw_debug, draw_progress, num_frames):
    morphogenesis = Morphogenesis(nodes, closed=is_circle, config=morphogenesis_config)

    if draw_debug:
        draw_force_fun = lambda p0, p1, mat_idx: draw_line(gp_frame, p0, p1, material_index=mat_idx)
        draw_segment_fun = lambda nodes, mat_idx: draw_segment(gp_frame, nodes, material_index=mat_idx,
                                                               draw_cyclic=is_circle)
    else:
        draw_force_fun = draw_segment_fun = None

    # Run and Draw Simulation
    gp_layer.frames.new(-1)
    for frame in range(num_frames):
        if frame % 10 == 0:
            print("Updating frame {}".format(frame))
        if draw_progress:
            gp_frame = gp_layer.frames.copy(gp_layer.frames[-1])
            gp_frame.frame_number = frame
        else:
            gp_frame = gp_layer.frames.new(frame)
        morphogenesis.update(draw_force=draw_force_fun, draw_segment=draw_segment_fun)
        # increase z pos
        nodes = np.array(morphogenesis.nodes)
        nodes += np.array([0, 0, frame*0.1])
        draw_segment(gp_frame, nodes, draw_cyclic=is_circle)


def run_morphogenesis_grid(nb_frames: int, nb_rows: int, nb_cols: int,
                           draw_progress=False, draw_debug=False):
    nb_nodes = 6
    bpy.context.scene.frame_end = nb_frames

    is_circle = True
    morphogenesis_config = {
        'VISIBILITY_RADIUS': 0.4,
        'REPULSION_FAC': 1 / 20,
        'ATTRACTION_FAC': 1 / 20,
        'SPLIT_DIST_THRESHOLD': 0.2,
        'RAND_OPTIMIZATION_FAC': 0,
        'SUBDIVISION_METHOD': 'BY_DISTANCE',
        'DIMENSIONS': 2
    }

    SPACING_FACTOR = 10
    visibility_radiuses = np.linspace(0.1, 1., nb_rows)
    split_dist_thresholds = np.linspace(0.2, 0.3, nb_cols)

    base_gp = get_grease_pencil()
    for row in range(nb_rows):
        for col in range(nb_cols):
            # Circle
            if is_circle:
                center = (row*SPACING_FACTOR, col*SPACING_FACTOR, 0)
                radius = 1
                angle = 2 * pi / nb_nodes

                nodes = []
                for i in range(nb_nodes):
                    x = center[0] + radius * cos(angle * i)
                    y = center[1] + radius * sin(angle * i)
                    z = 0#center[2] + (np.random.rand()-0.5)
                    nodes.append(np.array([x, y, z]))
            # Line
            else:
                nodes = [(np.array((x, 0, 0)) + (0.5 - np.random.rand(3))) * np.array([1., 1., 0.])
                         for x in np.linspace(1, 11, nb_nodes)]

            gp_layer = get_grease_pencil_layer(base_gp, "r_{}_c_{}".format(row, col), clear_layer=True)

            morphogenesis_config['VISIBILITY_RADIUS'] = visibility_radiuses[row]
            morphogenesis_config['SPLIT_DIST_THRESHOLD'] = split_dist_thresholds[col]

            print("##############")
            print("Row {}, Col {}".format(row, col))
            print("vis_rad {:.2f}, dist_threshold {:.2f}".format(visibility_radiuses[row], split_dist_thresholds[
                col]))
            run_morphogenesis(morphogenesis_config, gp_layer, nodes, is_circle, draw_debug, draw_progress, nb_frames)


run_morphogenesis_grid(nb_frames=10, nb_rows=3, nb_cols=3, draw_progress=True, draw_debug=False)


