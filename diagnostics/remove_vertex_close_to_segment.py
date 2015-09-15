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

sigma = 5.0

# Set working directory
#path = sys.path[0]  # Windows
#wd = os.path.dirname(__file__)  # Linux
wd = os.path.dirname("/home/babykitty/Work/Wetlands-Loss/data/test_area2/")

# Set shapefile path
shp_in_file = "wwi_dissolve2_simp2.0.shp"
shp_in_path = os.path.join(wd, shp_in_file)
shp_out_file = shp_in_file[:-4]+"_forced_simplify.shp"
shp_out_path = os.path.join(wd, shp_out_file)

#------------------------
# Prepare input data set
#------------------------

# Check if file exists
if not os.path.isfile(shp_in_path):
	print "Input shapefile does not exist."

driver = ogr.GetDriverByName('ESRI Shapefile')  # Get appropriate driver
shp_in_source = driver.Open(shp_in_path, gdalconst.GA_ReadOnly)  # Open the file using the driver

# Verify if the file was opened, if not exit
if shp_in_source is None:
	print 'Failed to open file'
	sys.exit(-1)

shp_in_layer = shp_in_source.GetLayer(0)  # Get first layer
feature_count = shp_in_layer.GetFeatureCount()  # Feature count


#-------------------------
# Prepare output data set
#-------------------------

# Check if file exists
if os.path.isfile(shp_out_path):
	print "Output shapefile already exists."
	sys.exit(-1)

# Create shapefile
shp_out_file = driver.CreateDataSource(shp_out_path)
shp_out_layer = shp_out_file.CreateLayer('foolayer',geom_type=ogr.wkbPolygon)

# Validate creation
if shp_out_layer is None:
	print "Could not create output layer."
	sys.exit(-1)

shp_out_def = shp_out_layer.GetLayerDefn() # Every feature in layer will have this


#---------------
# Find vertices
#---------------

def dist(ring1,ring2,point,next_point,ring_out):
	x,y,z = ring1.GetPoint(point)  # Get coords of first vertex
	u,v,w = ring2.GetPoint(next_point)  # Get coords of next vertex
	d = numpy.sqrt(((x-u)**2)+((y-v)**2))  # Find the distance between the vertices
	if d < sigma: print "Removed point",x,y,"because it was",d,"meters away from point",u,v
	else: 
		csv_out.write(str(x)+"\t"+str(y)+"\t"+str(u)+"\t"+str(v)+"\t"+str(d)+"\n")
		ring_out.AddPoint(x,y)
	return

def min_dist_to_line(v_0,v_1,v_2,ring_out):
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
		if not d_line < sigma:
			ring_out.AddPoint(x)
	else:  # If vertex 3 is not within bounding box of vertices 1 and 2 then it must not lie on segment, distance to segment is then the distance to the closest vertex of segment
		# Distance from vertext 0 to vertices 1 and 2
		d_v_1,d_v_2 = numpy.sqrt(((x_0-x_1)**2)+((y_0-y_1)**2)),numpy.sqrt(((x_0-x_2)**2)+((y_0-y_2)**2))
		return min(d_v_1,d_v_2)
	
for i in range(0,feature_count):  # Iterate over each feature

	# Get shapefile feature and set geom refs
	poly_feature = shp_in_layer.GetFeature(i)
	poly = poly_feature.GetGeometryRef()
	poly_out = ogr.Geometry(ogr.wkbPolygon)  # Create empty output polygon

	for linearring in range(0,poly.GetGeometryCount()):  # Iterate over each linear ring in polygon
		ring = poly.GetGeometryRef(linearring)
		ring_out = ogr.Geometry(ogr.wkbLinearRing)  # Create empty output ring

		for point in range(0,ring.GetPointCount()):  # Iterate over each point in linear ring
			if point != ring.GetPointCount()-1:
				for j in range(0,ring.GetPointCount()):
					if (j != point and j != point+1):

						dist(ring.GetPoint(j),ring.GetPoint(point),ring.GetPoint(point+1),ring_out)
			else:
				for j in range(0,ring.GetPointCount()):
					if (j != point and j != 0):
						dist(ring.GetPoint(j),ring.GetPoint(point),ring_out.GetPoint(0),ring.GetPoint(j),ring_out)  # On the last vertex of ring, distance to first non-removed vertex which can be found in "ring out"		

		ring_out.CloseRings()  # Make sure rings are closed.
		if ring_out.GetPointCount() < 4: continue  # Rings with less than four vertices are considered invalid topology
		poly_out.AddGeometry(ring_out)

	# Write polygon to shapefile
	shp_out_feature = ogr.Feature(shp_out_def)  	# Create empty feature
	shp_out_feature.SetGeometry(poly_out)  			# Create geometry
	shp_out_feature.SetFID(i)  						# Set fid
	shp_out_layer.CreateFeature(shp_out_feature)  	# Add feature to layer