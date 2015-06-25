# Import ogr and gdal depending on system
try:
	import ogr, osr, gdal
except:
	try:
		from osgeo import ogr, osr, gdal
	except: 
		print "Import of ogr/gdal failed."

# Import other needed modules
import numpy, os, sys, shutil, gdalconst


# Set working directory
path = os.path.dirname(__file__)

# Set paths for datasets
pls_path = os.path.join(path, "data/test_area/pls_wgs.shp")
wwi_path = os.path.join(path, "data/test_area/wwi_wgs_dissolve.shp")


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

# Get one feature to get geom ref later
pls_feature = pls_layer.GetFeature(0)

# Feature count
featureCount1 = pls_layer.GetFeatureCount()
print featureCount1


"""# Get feature
feature2 = pls_layer.GetFeature(0)
# Get feature geometry
poly = feature2.GetGeometryRef()
print poly
# Get access to the layer's non-spatial info: number of fields, field names, field types, etc.
featureDefn2 = pls_layer.GetLayerDefn()
print featureDefn2
# Get feature count
fieldCount2 = featureDefn2.GetFieldCount()
print fieldCount2"""

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
print featureCount2

#---------------------------
# Prepare intersection data
#---------------------------

# Create temp folder
temp_dir = os.path.join(path,"temp/")
if not os.path.exists(temp_dir):
	os.makedirs(temp_dir)
else:
	print temp_dir,"already exits. Please remove or rename."

# Create shapefile
dstshp = driver.CreateDataSource(os.path.join(temp_dir,"temp.shp"))
pls_notlost = dstshp.CreateLayer('foolayer',geom_type=ogr.wkbPoint)
if pls_notlost is None:
	print "Could not create output layer."
	sys.exit(-1)

pls_notlost_def = pls_notlost.GetLayerDefn() # Every feature in layer will have this

#----------------
# Intoduce error
#----------------

#---------------------------------
# PLS within/outside WWI wetlands
#---------------------------------

TrueCount = 0
FalseCount = 0
# Iterate through point features to find where points intersect WWI
for i in range(0, featureCount1):
	# Get PLS feature and set geom refs
	point_feature = pls_layer.GetFeature(i)
	point = point_feature.GetGeometryRef()
	poly = wwi_feature.GetGeometryRef()
	# Check if WWI intersects PLS point
	cross = poly.Intersects(point)
	# Count the number of intersects or nots
	geometry = point_feature.GetGeometryRef()
	if cross:
		TrueCount = TrueCount + 1
		# Add current PLS point to file
		pls_notlost_feature = ogr.Feature(pls_notlost_def) #create feature
		pls_notlost_feature.SetGeometry(geometry)  		   #add geometry
		pls_notlost_feature.SetFID(i) 			           #set id
		pls_notlost.CreateFeature(pls_notlost_feature) 	   #add feature to layer
	else:
		FalseCount = FalseCount + 1

# Diagonostic count
print "Wetlands not lost:", TrueCount
print "Wetlands lost:",FalseCount
print "Total wetlands:",TrueCount+FalseCount


#---------------------------
# Combine and export tables
#---------------------------


# Free memory
wwi_source = None
wwi_layer = None
pls_source = None
pls_layer = None
dstshp = None
pls_notlost = None
pls_notlost_feature = None

#shutil.rmtree(temp_dir)