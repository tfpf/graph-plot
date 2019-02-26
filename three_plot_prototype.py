#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as pp
import mpl_toolkits.mplot3d as mp

count_file = open('counter.txt')
graph_id = int(count_file.readline().strip()) + 1
count_file.close()

count_file = open('counter.txt', 'w')
count_file.write('%d\n' % graph_id)
count_file.close()

fig = pp.figure()
fig.canvas.set_window_title('graph_%x' % graph_id)
ax = pp.axes(projection = '3d')

x1 = np.linspace(-3 * np.pi, 5 * np.pi, 32894)
y1 = np.cos(x1)
z1 = np.random.rand(32894)

ax.plot3D(x1, y1, z1, 'k-', label = 'boobs', linewidth = 0.8)
ax.view_init(60, 35)
fig
