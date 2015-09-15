# Import other needed modules
import os, sys, csv, numpy
from datetime import datetime

# User variables
threshold = 20
input_csv_path = "/home/babykitty/Work/Wetlands-Loss/vertices.csv"  # This input needs to be the output of close_vertices.py
output_csv_path = "/home/babykitty/Work/Wetlands-Loss/min_dist_to_segments.csv"

# Check if csv's exist
if not os.path.isfile(input_csv_path):
	print input_csv_path,"does not exist."
	sys.exit(-1)
if os.path.isfile(output_csv_path):
	print output_csv_path,"already exists."
	sys.exit(-1)


def min_dist_to_line(v_0,v_1,v_2):
	# x,y for each vertex
	x_0, y_0 = float(v_0[1]),float(v_0[2])
	x_1, y_1 = float(v_1[1]),float(v_1[2])
	x_2, y_2 = float(v_2[1]),float(v_2[2])
	
	if int(numpy.sqrt(((x_1-x_2)**2))+((y_1-y_2)**2)) == 0: return numpy.sqrt(((x_0-x_1)**2)+((y_0-y_1)**2))
	# Slope and y-int for line conecting vertex 1 and 2
	if x_1-x_2 == 0: m_12 = 1  # If the distance between x 1 and 2 is zero, proceeding would divide by zero so this catches that
	else: m_12 = abs(y_1-y_2)/abs(x_1-x_2)
	b_12 = y_1 - (m_12*x_1)
	# Slope and y-int for line intersecting vertex 0, vertex 3 is intersection of line 12 and line 03
	if m_12 == 0: m_03 = 1
	else: m_03 = -(1/m_12)
	b_03 = y_0 + (m_03*x_0)
	# Find vertex 3, i.e., the intersection of the two lines
	x_3 = (b_03-b_12)/(m_12-m_03)
	y_3 = (m_03*x_3)+b_03
	# Distance from vertex 0 to line, i.e., vertex 3
	d_line = numpy.sqrt(((x_0-x_3)**2)+((y_0-y_3)**2))
	# Check that vertex 3 is along segment conecting vertices 1 and 2
	if ((min(x_1,x_2) < x_3 < max(x_1,x_2)) and (min(y_1,y_2) < y_3 < max(y_1,y_2))):
		return d_line
	else:  # If vertex 3 is not within bounding box of vertices 1 and 2 then it must not lie on segment, distance to segment is then the distance to the closest vertex of segment
		# Distance from vertext 0 to vertices 1 and 2
		d_v_1,d_v_2 = numpy.sqrt(((x_0-x_1)**2)+((y_0-y_1)**2)),numpy.sqrt(((x_0-x_2)**2)+((y_0-y_2)**2))
		return min(d_v_1,d_v_2)
	

# Open input csv file
with open(input_csv_path,"rb") as input_csv:
	lines = list(csv.reader(input_csv,delimiter="\t"))
	#lines = lines[0:5]
	print "Creating sorted sets...                                 ",str(datetime.now())
	fids = sorted(set(map(lambda x:x[0],lines)))
	features = [[line for line in lines if line[0]==fid] for fid in fids]
	print "Sets created. Calculating minimum distance to segment...",str(datetime.now())

# Open output csv file
output_csv = open(output_csv_path,"a")

# Find min length from point to segment
for i in range(0,len(features)):  # For each feature
	feature = features[i]
	for j in range(0,len(feature)):  # For each vertex, grab vertex and next vertex
		if not j == len(feature)-1:  # Normal case: distance between point and next point
			for h in range(0,len(feature)):  # For each vertex other than the two that make the segment
				if (h != j and h != j+1):
					min_dist = min_dist_to_line(feature[h],feature[j],feature[j+1])
					if min_dist < threshold: output_csv.write(str(i)+"\t"+str(j)+"\t"+str(j+1)+"\t"+str(h)+"\t"+str(min_dist)+"\n")

		else:  # Special case: distance between last point and first point
			for h in range(0,len(feature)):
				if (h != j and h != 0):
					min_dist = min_dist_to_line(feature[h],feature[j],feature[0])
					if min_dist < threshold: output_csv.write(str(i)+"\t"+str(j)+"\t"+str(0)+"\t"+str(h)+"\t"+str(min_dist)+"\n")

print "Finished.                                               ",str(datetime.now())

# Close csv
input_csv.close()
output_csv.close()