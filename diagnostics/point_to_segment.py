# Import ogr and gdal depending on system
try:
	import ogr, osr, gdal
except:
	try:
		from osgeo import ogr, osr, gdal
	except: 
		print "Import of ogr/gdal failed."

# Import other needed modules
import os, sys, csv, numpy
from datetime import datetime

print "Start:                                                  ",str(datetime.now())

# User variables
threshold = 20
vertices_csv_path = "/home/babykitty/Work/Wetlands-Loss/vertices.csv"  # This input needs to be the output of close_vertices.py
segments_csv_path = "/home/babykitty/Work/Wetlands-Loss/min_dist_to_segments.csv"
shp_path = "/home/babykitty/Work/Wetlands-Loss/data/test_area/wwi_dissolve2_simp2.0.shp"

# Check if csv's exist
if os.path.isfile(vertices_csv_path):
	print vertices_csv_path,"already exists."
	sys.exit(-1)
if os.path.isfile(segments_csv_path):
	print segments_csv_path,"already exists."
	sys.exit(-1)


def min_dist_to_line(v_0,v_1,v_2):
	# x,y for each vertex
	x_0, y_0 = float(v_0[0]),float(v_0[1])
	x_1, y_1 = float(v_1[0]),float(v_1[1])
	x_2, y_2 = float(v_2[0]),float(v_2[1])
	
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
		# Distance from vertex 0 to vertices 1 and 2
		d_v_1,d_v_2 = numpy.sqrt(((x_0-x_1)**2)+((y_0-y_1)**2)),numpy.sqrt(((x_0-x_2)**2)+((y_0-y_2)**2))
		return min(d_v_1,d_v_2)


#------------------------
# Prepare input data set
#------------------------

# Check if file exists
if not os.path.isfile(shp_path):
	print "Shapefile does not exist."

driver = ogr.GetDriverByName('ESRI Shapefile')  # Get appropriate driver
shp_source = driver.Open(shp_path, 0)  # Open the file using the driver

# Verify if the file was opened, if not exit
if shp_source is None:
	print 'Failed to open file'
	sys.exit(-1)

shp_layer = shp_source.GetLayer(0)  # Get first layer
feature_count = shp_layer.GetFeatureCount()  # Feature count

#---------------
# Find vertices
#---------------

# Open csv file
vertices_csv = open(vertices_csv_path,"a")
segments_csv = open(segments_csv_path,"a")

for i in range(0,feature_count):  # Iterate over each feature

	lines = []  # Create empty list lines to write to csv

	# Get shapefile feature and set geom refs
	poly_feature = shp_layer.GetFeature(i)
	poly = poly_feature.GetGeometryRef()

	for linearring in range(0,poly.GetGeometryCount()):  # Iterate over each linear ring in polygon
		ring = poly.GetGeometryRef(linearring)

		for point in range(0,ring.GetPointCount()):  # Iterate over each point in linear ring, create new points randomly sampled from gaussian distribution
			x,y,z = ring.GetPoint(point)
			lines.append([i,x,y])


	# Distance between points
	for j in range(0,len(lines)):
		if not j == len(lines)-1:  # Normal case: distance between point and next point
			d = numpy.sqrt(((lines[j][1]-lines[j+1][1])**2)+((lines[j][2]-lines[j+1][2])**2))
			lines[j].append(d)
			vertices_csv.write(str(lines[j][0])+"\t"+str(lines[j][1])+"\t"+str(lines[j][2])+"\t"+str(lines[j+1][1])+"\t"+str(lines[j+1][2])+"\t"+str(lines[j][3])+"\n")  # print i,x1,y1,x2,y2,distance between points 1 and 2
		else:  # Special case: distance between last point and first point
			d = str(numpy.sqrt(((lines[j][1]-lines[0][1])**2)+((lines[j][2]-lines[0][2])**2)))
			lines[j].append(d)
			vertices_csv.write(str(lines[j][0])+"\t"+str(lines[j][1])+"\t"+str(lines[j][2])+"\t"+str(lines[0][1])+"\t"+str(lines[0][2])+"\t"+str(lines[j][3])+"\n")  # print i,x1,y1,x2,y2,distance between points 1 and 2	


	# Find min length from point to segment
	for j in range(0,len(lines)):  # For each vertex, grab vertex and next vertex
		if not j == len(lines)-1:  # Normal case: distance between point and next point
			for h in range(0,len(lines)):  # For each vertex other than the two that make the segment
				if (h != j and h != j+1):
					min_dist = min_dist_to_line([lines[h][1],lines[h][2]],[lines[j][1],lines[j][2]],[lines[j+1][1],lines[j+1][2]])
					if min_dist < threshold: segments_csv.write(str(i)+"\t"+str(j)+"\t"+str(j+1)+"\t"+str(h)+"\t"+str(min_dist)+"\n")

		else:  # Special case: distance between last point and first point
			for h in range(0,len(lines)):
				if (h != j and h != 0):
					min_dist = min_dist_to_line([lines[h][1],lines[h][2]],[lines[j][1],lines[j][2]],[lines[0][1],lines[0][2]])
					if min_dist < threshold: segments_csv.write(str(i)+"\t"+str(j)+"\t"+str(0)+"\t"+str(h)+"\t"+str(min_dist)+"\n")

print "Finish:                                                 ",str(datetime.now())

# Close csv
vertices_csv.close()
segments_csv.close()