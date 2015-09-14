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

# Open csv file
csv_path = os.path.join(wd, "vertices.csv")
if os.path.isfile(csv_path):
	print csv_path,"already exits. Cannot ouput results there."
	sys.exit(-1)
csv_out = open(csv_path,"a")

# Write header to file
csv_out.write("x\ty\tu\tv\td\n")

def dist(ring1,ring2,point,next_point,ring_out):
	x,y,z = ring1.GetPoint(point)  # Get coords of first vertex
	u,v,w = ring2.GetPoint(next_point)  # Get coords of next vertex
	d = numpy.sqrt(((x-u)**2)+((y-v)**2))  # Find the distance between the vertices
	if d < sigma: print "Removed point",x,y,"because it was",d,"meters away from point",u,v
	else: 
		csv_out.write(str(x)+"\t"+str(y)+"\t"+str(u)+"\t"+str(v)+"\t"+str(d)+"\n")
		ring_out.AddPoint(x,y)
	return
	
for i in range(0,feature_count):  # Iterate over each feature

	# Get shapefile feature and set geom refs
	poly_feature = shp_in_layer.GetFeature(i)
	poly = poly_feature.GetGeometryRef()
	poly_out = ogr.Geometry(ogr.wkbPolygon)  # Create empty output polygon

	for linearring in range(0,poly.GetGeometryCount()):  # Iterate over each linear ring in polygon
		ring = poly.GetGeometryRef(linearring)
		ring_out = ogr.Geometry(ogr.wkbLinearRing)  # Create empty output ring

		for point in range(0,ring.GetPointCount()):  # Iterate over each point in linear ring
			if point != ring.GetPointCount()-1: dist(ring,ring,point,point+1,ring_out)
			else: dist(ring,ring_out,point,0,ring_out)  # On the last vertex of ring, distance to first non-removed vertex which can be found in "ring out"		

		ring_out.CloseRings()  # Make sure rings are closed.
		poly_out.AddGeometry(ring_out)

	# Write polygon to shapefile
	shp_out_feature = ogr.Feature(shp_out_def)  	# Create empty feature
	shp_out_feature.SetGeometry(poly_out)  			# Create geometry
	shp_out_feature.SetFID(i)  						# Set fid
	shp_out_layer.CreateFeature(shp_out_feature)  	# Add feature to layer

csv_out.close()  # Close csv