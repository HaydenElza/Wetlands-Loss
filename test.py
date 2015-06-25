# Import ogr and gdal depending on system
try:
	import ogr, osr, gdal
except:
	try:
		from osgeo import ogr, osr, gdal
	except: 
		print "Import of ogr/gdal failed."

# Import other needed modules
import numpy, os, sys, shutil, gdalconst, csv


# Set working directory
path = os.path.dirname(__file__)

#----------------
# User Variables
#----------------

interations = 5

# Set paths for datasets
pls_path = os.path.join(path, "data/test_area/pls.shp")
wwi_path = os.path.join(path, "data/test_area/wwi.shp")

#----------------


# Addition of normally distributed error to data as a part of the Monte Carlo simulation
def error_band(dataset,geom,stdev):  # geom: point or polygon, stdev: the standard deviation of the dataset's spatial accuracy
	for feature in layer:
		pass
	return

# Determine whether PLS points are within or outside of WWI polygons
def in_out(pls,wwi):
	return


#----------------------------------------------------------------------------
# Main
#----------------------------------------------------------------------------

#------------------
# Prepare PLS data
#------------------

# Check if file exists
if not os.path.isfile(pls_path):
	print "File does not exist."

# Get appropriate driver
driver = ogr.GetDriverByName('ESRI Shapefile')

# Open the file using the driver
pls_source = driver.Open(pls_path, gdalconst.GA_ReadOnly)

# Verify if the file was opened, if not exit
if pls_source is None:
	print 'Failed to open file'
	sys.exit(-1)

# Get first layer
pls_layer = pls_source.GetLayer(0)

# Feature count
featureCount1 = pls_layer.GetFeatureCount()


#------------------
# Prepare WWI data
#------------------

# Check if file exists
if not os.path.isfile(wwi_path):
	print "File does not exist."

# Open the file using the driver
wwi_source = driver.Open(wwi_path, gdalconst.GA_ReadOnly)

# Verify if the file was opened, if not exit
if wwi_source is None:
	print 'Failed to open file'
	sys.exit(-1)

# Get first layer
wwi_layer = wwi_source.GetLayer(0)

# Get one feature to get geom ref later
wwi_feature = wwi_layer.GetFeature(0)

# Feature count
featureCount2 = wwi_layer.GetFeatureCount()


#----------------------------------------------------------------------------------------------

#---------------
# Set variables
#---------------
pls_accuracy = 15.24/3  # Standard deviation of positional accuracy in meters


# Create temp folder
temp_dir = os.path.join(path,"temp/")
if not os.path.exists(temp_dir):
	os.makedirs(temp_dir)
else:
	print temp_dir,"already exits. Please remove or rename."



#------------------------
# Prepare prime PLS data
#------------------------

# Create shapefile
dstshp = driver.CreateDataSource(os.path.join(temp_dir,"pls_prime.shp"))
pls_prime = dstshp.CreateLayer('foolayer',geom_type=ogr.wkbPoint)

# Validate creation
if pls_prime is None:
	print "Could not create output layer."
	sys.exit(-1)

# Create fields
field_corn_id = ogr.FieldDefn("corn_id", ogr.OFTString)
field_corn_id.SetWidth(11)
pls_prime.CreateField(field_corn_id)

pls_prime_def = pls_prime.GetLayerDefn() # Every feature in layer will have this

#------------------------
# Prepare prime WWI data
#------------------------

# Create shapefile
dstshp = driver.CreateDataSource(os.path.join(temp_dir,"wwi_prime.shp"))
wwi_prime = dstshp.CreateLayer('foolayer',geom_type=ogr.wkbPolygon)

# Validate creation
if wwi_prime is None:
	print "Could not create output layer."
	sys.exit(-1)

wwi_prime_def = wwi_prime.GetLayerDefn() # Every feature in layer will have this
"""
#--------------------
# Simulate PLS prime
#--------------------

for i in range(0, featureCount1):
	# Get PLS feature and set geom refs
	point_feature = pls_layer.GetFeature(i)
	point = point_feature.GetGeometryRef()

	# Create point_prime geometry
	point_prime = ogr.Geometry(ogr.wkbPoint)
	x_prime = float(numpy.random.normal(point.GetX(),float(pls_accuracy),1))
	y_prime = float(numpy.random.normal(point.GetY(),float(pls_accuracy),1))
	point_prime.AddPoint(x_prime,y_prime)  # Add geometry
	""""""
	# Print orginal coords, new coords, and difference between the two
	print "X ",point.GetX(),
	print "\t\tY ",point.GetY()
	print "X'",x_prime,
	print "\tY'",y_prime
	print "Dx",point.GetX()-x_prime,
	print "\tDy",point.GetY()-y_prime
	print ""
	""""""
	# Create pls_prime geometry and fields
	pls_prime_feature = ogr.Feature(pls_prime_def)  # Create empty feature
	pls_prime_feature.SetGeometry(point_prime)  # Create geometry
	pls_prime_feature.SetFID(i)  # Set fid
	pls_prime_feature.SetField("corn_id",str(point_feature.GetField("CORN_ID"))[:11])  # Set field to CORN_ID
	pls_prime.CreateFeature(pls_prime_feature)  # Add feature to layer
"""
#--------------------
# Simulate WWI prime
#--------------------
for i in range(0, 5):
	# Get WWI feature and set geom refs
	poly_feature = wwi_layer.GetFeature(i)
	poly = poly_feature.GetGeometryRef()
	
	for linearring in range(0,poly.GetGeometryCount()):
		ring = poly.GetGeometryRef(linearring)
		print ring

		for point in range(0,ring.GetGeometryCount()):
			pnt = ring.GetGeometryRef(point)
			print pnt

	print poly.GetGeometryType(),poly.GetGeometryCount()
	point = poly.GetGeometryRef(0)
	print point
	print point.GetPointCount()
	print ""

"""	# Create poly_prime geometry
	poly_prime = ogr.Geometry(ogr.wkbPolygon)
	x_prime = float(numpy.random.normal(poly.GetX(),float(pls_accuracy),1))
	y_prime = float(numpy.random.normal(poly.GetY(),float(pls_accuracy),1))
	poly_prime.Addpoly(x_prime,y_prime)  # Add geometry
	
	# Print orginal coords, new coords, and difference between the two
	print "X ",poly.GetX(),
	print "\t\tY ",poly.GetY()
	print "X'",x_prime,
	print "\tY'",y_prime
	print "Dx",poly.GetX()-x_prime,
	print "\tDy",poly.GetY()-y_prime
	print ""
	
	# Create pls_prime geometry and fields
	pls_prime_feature = ogr.Feature(pls_prime_def)  # Create empty feature
	pls_prime_feature.SetGeometry(point_prime)  # Create geometry
	pls_prime_feature.SetFID(i)  # Set fid
	pls_prime.CreateFeature(pls_prime_feature)  # Add feature to layer
"""



shutil.rmtree(temp_dir)