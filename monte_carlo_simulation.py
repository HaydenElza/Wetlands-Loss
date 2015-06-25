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
pls_path = os.path.join(path, "data/test_area/pls_wgs.shp")
wwi_path = os.path.join(path, "data/test_area/wwi_wgs_dissolve.shp")

# Create output folder, exit if it already exists
output_dir = os.path.join(path,"output/")
if not os.path.exists(output_dir):
	os.makedirs(output_dir)
else:
	print output_dir,"already exits. Cannot ouput results there."
	sys.exit(-1)

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


#---------------------------
# Prepare intersection data
#---------------------------
"""
# Create temp folder
temp_dir = os.path.join(path,"temp/")
if not os.path.exists(temp_dir):
	os.makedirs(temp_dir)
else:
	print temp_dir,"already exits. Please remove or rename."

# Create shapefile
dstshp = driver.CreateDataSource(os.path.join(temp_dir,"temp.shp"))
pls_notlost = dstshp.CreateLayer('foolayer',geom_type=ogr.wkbPoint)

# Validate creation
if pls_notlost is None:
	print "Could not create output layer."
	sys.exit(-1)

# Create fields
field_corn_id = ogr.FieldDefn("corn_id", ogr.OFTString)
field_corn_id.SetWidth(11)
pls_notlost.CreateField(field_corn_id)
pls_notlost.CreateField(ogr.FieldDefn("lost", ogr.OFTInteger))
field_iter = ogr.FieldDefn("iter", ogr.OFTString)
field_iter.SetWidth(6)
pls_notlost.CreateField(field_iter)

pls_notlost_def = pls_notlost.GetLayerDefn() # Every feature in layer will have this
"""

for iteration in range(0,interations):
	#----------------
	# Intoduce error
	#----------------

	#---------------------------------
	# PLS within/outside WWI wetlands
	#---------------------------------
	TrueCount = 0
	FalseCount = 0

	# Set ouput csv file
	csv_path = os.path.join(path, "output/results_"+str(iteration)+".csv")
	csv_out = open(csv_path,"a")

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

			# Add line to csv
			csv_out.write(str(point_feature.GetField("CORN_ID"))[:11]+",1,"+str(iteration)+"\n")

			# Add current PLS point to file
			"""pls_notlost_feature = ogr.Feature(pls_notlost_def) # Create feature
			pls_notlost_feature.SetGeometry(geometry)  		   # Add geometry
			pls_notlost_feature.SetFID(i) 			           # Set id
			pls_notlost_feature.SetField("corn_id",str(point_feature.GetField("CORN_ID"))[:11])  # Set field to CORN_ID
			pls_notlost_feature.SetField("lost", 1)            # Set field lost to 1
			pls_notlost_feature.SetField("iter", iteration)    # Set field iter to iteration number
			pls_notlost.CreateFeature(pls_notlost_feature) 	   # Add feature to layer"""
			
		else:
			FalseCount = FalseCount + 1

	# Diagonostic count
	print "Wetlands not lost:", TrueCount
	print "Wetlands lost:",FalseCount
	print "Total wetlands:",TrueCount+FalseCount

	# Close csv
	csv_out.close()


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