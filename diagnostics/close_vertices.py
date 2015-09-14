# Import ogr and gdal depending on system
try:
	import ogr, osr, gdal
except:
	try:
		from osgeo import ogr, osr, gdal
	except: 
		print "Import of ogr/gdal failed."

# Import other needed modules
import os, sys, gdalconst, csv, numpy

# Set working directory
#path = sys.path[0]  # Windows
wd = os.path.dirname(__file__)  # Linux
wd = os.path.dirname("/home/babykitty/Work/Wetlands-Loss/")

# Set shapefile path
shp_file = "data/test_area/wwi_dissolve2_simp2.0.shp"
shp_path = os.path.join(wd, shp_file)

#------------------------
# Prepare input data set
#------------------------

# Check if file exists
if not os.path.isfile(shp_path):
	print "Shapefile does not exist."

driver = ogr.GetDriverByName('ESRI Shapefile')  # Get appropriate driver
shp_source = driver.Open(shp_path, gdalconst.GA_ReadOnly)  # Open the file using the driver

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
csv_path = os.path.join(wd, "vertices.csv")
if os.path.isfile(csv_path):
	print csv_path,"already exits. Cannot ouput results there."
	sys.exit(-1)
csv_out = open(csv_path,"a")

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
			csv_out.write(str(lines[j][0])+"\t"+str(lines[j][1])+"\t"+str(lines[j][2])+"\t"+str(lines[j][3])+"\n")	
		else:  # Special case: distance between last point and first point
			d = str(numpy.sqrt(((lines[j][1]-lines[0][1])**2)+((lines[j][2]-lines[0][2])**2)))
			lines[j].append(d)
			csv_out.write(str(lines[j][0])+"\t"+str(lines[j][1])+"\t"+str(lines[j][2])+"\t"+str(lines[j][3])+"\n")			

# Close csv
csv_out.close()