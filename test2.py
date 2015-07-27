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


#----------------
# User Variables
#----------------
interations = 1
pls_accuracy = 15.24#/3  # Standard deviation of positional accuracy in meters
wwi_ortho_accuracy = 5/3
wwi_nonortho_accuracy = 15/3
nwi_lacrosse_accuracy = 6/3
nwi_others_accuracy = 15/3
pls_path = "data/test_area/pls.shp"
wwi_ortho_path = "data/test_area/wwi_dissolve2_simp2.0.shp"
wwi_nonortho_path = "data/test_area/wwi_dissolve2_simp2.0.shp"
nwi_lacrosse_path = "data/test_area/wwi_dissolve2_simp2.0.shp"
nwi_others_path = "data/test_area/wwi_dissolve2_simp2.0.shp"
output_dir = "output/"
suppress_ogr_errors = False  # ogr.IsValid() is used to check for valid geom and causes many warnings, suppressing them should increase speed, use False for debug
#----------------


# Set working directory
#path = sys.path[0]  # Windows
path = os.path.dirname(__file__)  # Linux

# Set paths for datasets
pls_path = os.path.join(path, pls_path)
wwi_ortho_path = os.path.join(path, wwi_ortho_path)
wwi_nonortho_path = os.path.join(path, wwi_nonortho_path)
nwi_lacrosse_path = os.path.join(path, nwi_lacrosse_path)
nwi_others_path = os.path.join(path, nwi_others_path)

# Create output folder, exit if it already exists
output_dir = os.path.join(path, output_dir)
if not os.path.exists(output_dir):
	os.makedirs(output_dir)
else:
	print output_dir,"already exits. Cannot ouput results there."
	sys.exit(-1)

# Suppress gdal/ogr errors if suppress_ogr_errors is True, this is used because ogr.IsValid() is used to check for valid geom and causes many warnings
if suppress_ogr_errors: gdal.PushErrorHandler('CPLQuietErrorHandler')


#----------------------------------------------------------------------------
# Main
#----------------------------------------------------------------------------

#------------------
# Prepare PLS data
#------------------

# Check if file exists
if not os.path.isfile(pls_path):
	print "PLS does not exist."

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


#------------------------
# Prepare WWI ortho data
#------------------------

# Check if file exists
if not os.path.isfile(wwi_ortho_path):
	print "WWI Ortho does not exist."

# Open the file using the driver
wwi_ortho_source = driver.Open(wwi_ortho_path, gdalconst.GA_ReadOnly)

# Verify if the file was opened, if not exit
if wwi_ortho_source is None:
	print 'Failed to open file'
	sys.exit(-1)

# Get first layer
wwi_ortho_layer = wwi_ortho_source.GetLayer(0)

# Get one feature to get geom ref later
wwi_ortho_feature = wwi_ortho_layer.GetFeature(0)

# Feature count
featureCount2 = wwi_ortho_layer.GetFeatureCount()


#---------------------------
# Prepare WWI nonortho data
#---------------------------

# Check if file exists
if not os.path.isfile(wwi_nonortho_path):
	print "WWI NonOrtho does not exist."

# Open the file using the driver
wwi_nonortho_source = driver.Open(wwi_nonortho_path, gdalconst.GA_ReadOnly)

# Verify if the file was opened, if not exit
if wwi_nonortho_source is None:
	print 'Failed to open file'
	sys.exit(-1)

# Get first layer
wwi_nonortho_layer = wwi_nonortho_source.GetLayer(0)

# Get one feature to get geom ref later
wwi_nonortho_feature = wwi_nonortho_layer.GetFeature(0)

# Feature count
featureCount3 = wwi_nonortho_layer.GetFeatureCount()

#----------------------------
# Prepare NWI La Crosse data
#----------------------------

# Check if file exists
if not os.path.isfile(nwi_lacrosse_path):
	print "NWI lacrosse does not exist."

# Open the file using the driver
nwi_lacrosse_source = driver.Open(nwi_lacrosse_path, gdalconst.GA_ReadOnly)

# Verify if the file was opened, if not exit
if nwi_lacrosse_source is None:
	print 'Failed to open file'
	sys.exit(-1)

# Get first layer
nwi_lacrosse_layer = nwi_lacrosse_source.GetLayer(0)

# Get one feature to get geom ref later
nwi_lacrosse_feature = nwi_lacrosse_layer.GetFeature(0)

# Feature count
featureCount4 = nwi_lacrosse_layer.GetFeatureCount()

#-------------------------
# Prepare NWI Others data
#-------------------------

# Check if file exists
if not os.path.isfile(nwi_others_path):
	print "NWI others does not exist."

# Open the file using the driver
nwi_others_source = driver.Open(nwi_others_path, gdalconst.GA_ReadOnly)

# Verify if the file was opened, if not exit
if nwi_others_source is None:
	print 'Failed to open file'
	sys.exit(-1)

# Get first layer
nwi_others_layer = nwi_others_source.GetLayer(0)

# Get one feature to get geom ref later
nwi_others_feature = nwi_others_layer.GetFeature(0)

# Feature count
featureCount5 = nwi_others_layer.GetFeatureCount()




#----------------------------------------------------------------------------------
# Intoduce error
#----------------------------------------------------------------------------------

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
pls_prime_dst = driver.CreateDataSource(os.path.join(temp_dir,"pls_prime.shp"))
pls_prime = pls_prime_dst.CreateLayer('foolayer',geom_type=ogr.wkbPoint)

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
# Prepare WWI prime data
#------------------------

# Create shapefile
wwi_prime_dst = driver.CreateDataSource(os.path.join(temp_dir,"wwi_prime.shp"))
wwi_prime = wwi_prime_dst.CreateLayer('foolayer',geom_type=ogr.wkbPolygon)

# Validate creation
if wwi_prime is None:
	print "Could not create output layer."
	sys.exit(-1)

wwi_prime_def = wwi_prime.GetLayerDefn() # Every feature in layer will have this

fid = 0  # This is to track the FID between both ortho and nonortho datasets


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
	
	# Create pls_prime geometry and fields
	pls_prime_feature = ogr.Feature(pls_prime_def)  # Create empty feature
	pls_prime_feature.SetGeometry(point_prime)  # Create geometry
	pls_prime_feature.SetFID(i)  # Set fid
	pls_prime_feature.SetField("corn_id",str(point_feature.GetField("CORN_ID"))[:11])  # Set field to CORN_ID
	pls_prime.CreateFeature(pls_prime_feature)  # Add feature to layer



#######################################################################################
#--------------------------
# Simulate WWI ortho prime
#--------------------------
# Iterate over each feature
for i in range(0,featureCount2):
	# Get WWI feature and set geom refs
	poly_feature = wwi_ortho_layer.GetFeature(i)
	poly = poly_feature.GetGeometryRef()
	
	valid = False
	while (not valid):
		poly_prime = None
		poly_prime = ogr.Geometry(ogr.wkbPolygon)

		# Iterate over each linear ring in polygon
		for linearring in range(0,poly.GetGeometryCount()):
			# Get each ring and create a prime ring to add prime points to
			ring = poly.GetGeometryRef(linearring)
			ring_prime = ogr.Geometry(ogr.wkbLinearRing)

			# Iterate over each point in linear ring, create new points randomly sampled from gaussian distribution
			for point in range(0,ring.GetPointCount()):
				# Get coordinates from point
				x,y,z = ring.GetPoint(point)
				# Create new points randomly sampled from gaussian distribution
				x_prime = float(numpy.random.normal(x,float(wwi_ortho_accuracy),1))
				y_prime = float(numpy.random.normal(y,float(wwi_ortho_accuracy),1))
				# Add new points to ring
				ring_prime.AddPoint(x_prime,y_prime)

			# Close new ring and add to polygon
			ring_prime.CloseRings()
			poly_prime.AddGeometry(ring_prime)

		valid = poly_prime.IsValid()

	# Write polygon to shapefile
	wwi_prime_feature = ogr.Feature(wwi_prime_def)  # Create empty feature
	wwi_prime_feature.SetGeometry(poly_prime)  # Create geometry
	wwi_prime_feature.SetFID(fid)  # Set fid
	wwi_prime.CreateFeature(wwi_prime_feature)  # Add feature to layer
	fid += 1  # Add one to the fid

	wwi_prime_feature = None

# Remove temp directory
shutil.rmtree(temp_dir)

