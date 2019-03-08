#!/usr/bin/env python3

import matplotlib.pyplot as pp
import numpy as np

################################################################################

# configure the plot to appear like an XKCD plot
pp.xkcd()

# set up a window to display the graph
# window title is a number obtained from 'counter.txt'
fig = pp.figure()
with open('counter.txt') as count_file:
	graph_id = int(count_file.readline().strip())
fig.canvas.set_window_title('graph_{}'.format(graph_id))
with open('counter.txt', 'w') as count_file:
	print('{}'.format(graph_id + 1), file = count_file)
ax = fig.add_subplot(1, 1, 1)

################################################################################

x1 = np.linspace(0, 10, 1000)
y1 = 0.1 * np.random.randn(1000) + 8
y1[400 : 600] = 0
ax.plot(x1, y1, 'k-', label = r'trends of supernatural miracles', linewidth = 0.8)

################################################################################

ax.legend(loc = 'best')
# ax.set_xlabel('time')
ax.set_xticklabels(['invention of\nthe camera', 'invention of image\nediting software'])
ax.set_xticks([4, 6])
ax.set_ylabel('frequency of miracles')
# ax.set_yticklabels([])
ax.set_yticks([])
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.set_title('How the claims of supernatural occurrences have changed')
ax.xaxis.set_ticks_position('bottom')

pp.show()
