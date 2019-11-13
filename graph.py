from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
import csv

fig = plt.figure()
ax = plt.axes(projection='3d')

x = []
y = []
z = []
with open("csvfile.csv") as data:
    datum = csv.reader(data)
    i = 0
    for row in datum:
        if i != 0:
            x.append(int(row[6]))
            y.append(int(row[4]))
            z.append(int(row[5]))
        i+=1
        #print(row)
print("got to scatter")
#plt.scatter(y, z, marker='o');
print("got to show")
#plt.show()


ax = plt.axes(projection='3d')

ax.scatter3D(x, y, z);
plt.show()