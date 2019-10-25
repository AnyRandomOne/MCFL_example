from sys import argv
import matplotlib.pyplot as plt
from matplotlib.lines  import Line2D

f_in = argv[1]
f = open(f_in)
x_value = []
y_value = []

for row in f:
    l = row.split(',')
    if len(l) < 3:
        continue
    x_value.append(float(l[1]))
    y_value.append(float(l[2]))

line1 = [(0,0), (6,6)]
(line1_x, line1_y)= zip(*line1)

figure, ax = plt.subplots()
ax.add_line(Line2D(line1_x, line1_y, linewidth=1, color='red'))

plt.scatter(x_value, y_value)
    
plt.axis([0, 7, 0, 7])
plt.savefig(argv[2])    
