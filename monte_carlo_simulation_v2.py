# Import ogr and gdal depending on system
try:
	import ogr, gdal
except:
	try:
		from osgeo import ogr, gdal
	except: 
		print "Import of ogr/gdal failed."

# Import other needed modules
import numpy, os, sys, shutil, csv, time


#----------------
# User Variables
#----------------
interations = 1
pls_accuracy = 15.24/3  # Standard deviation of positional accuracy in meters
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
suppress_ogr_errors = True  # ogr.IsValid() is used to check for valid geom and causes many warnings, suppressing them should increase speed, use False for debug
#----------------


def open_data(driver,path,name):
	# Check if file exists
	if not os.path.isfile(path): print name,"file does not exist."

	# Open the file using the driver
	source = driver.Open(path, 0)

	# Verify if the file was opened, if not exit
	if source is None:
		print "Failed to open",name,"file."
		sys.exit(-1)

	return source

def get_layer(source):
	# Get first layer
	layer = source.GetLayer(0)

	# Feature count
	feature_count = layer.GetFeatureCount()

	return layer,feature_count

def simulate_poly(feature_count,layer,accuracy,layer_def,fid,wwi_prime):
	for i in range(0,feature_count):
		# Get WWI feature and set geom refs
		poly_feature = layer.GetFeature(i)
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
				for point in range(0,ring.GetPointCount()-1):
					# Get coordinates from point
					x,y,z = ring.GetPoint(point)
					# Create new points randomly sampled from gaussian distribution
					x_prime = float(numpy.random.normal(x,float(accuracy),1))
					y_prime = float(numpy.random.normal(y,float(accuracy),1))
					# Add new points to ring
					ring_prime.AddPoint(x_prime,y_prime)

				# Close new ring and add to polygon
				ring_prime.CloseRings()
				poly_prime.AddGeometry(ring_prime)

			valid = True #poly_prime.IsValid()

		# Write polygon to shapefile
		wwi_prime_feature = ogr.Feature(layer_def)  # Create empty feature
		wwi_prime_feature.SetGeometry(poly_prime)  # Create geometry
		wwi_prime_feature.SetFID(fid)  # Set fid
		wwi_prime.CreateFeature(wwi_prime_feature)  # Add feature to layer
		fid += 1  # Add one to the fid
	
	wwi_prime_feature = None

	return fid,wwi_prime


#----------------------------------------------------------------------------
# Main
#----------------------------------------------------------------------------

t0 = time.clock()

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

#-------------------------------------------------------------------------------

# Get shapefile driver
driver = ogr.GetDriverByName('ESRI Shapefile')

# Prepare PLS data
pls_source = open_data(driver,pls_path,"PLS")
pls_layer,feature_count_1 = get_layer(pls_source)

# Prepare WWI ortho data
wwi_ortho_source = open_data(driver,wwi_ortho_path,"WWI Ortho")
wwi_ortho_layer,feature_count_2 = get_layer(wwi_ortho_source)

# Prepare WWI nonortho data
wwi_nonortho_source = open_data(driver,wwi_nonortho_path,"WWI Nonortho")
wwi_nonortho_layer,feature_count_3 = get_layer(wwi_nonortho_source)

# Prepare NWI La Crosse data
nwi_lacrosse_source = open_data(driver,nwi_lacrosse_path,"NWI La Crosse")
nwi_lacrosse_layer,feature_count_4 = get_layer(nwi_lacrosse_source)

# Prepare NWI Others data
nwi_others_source = open_data(driver,nwi_others_path,"NWI Others")
nwi_others_layer,feature_count_5 = get_layer(nwi_others_source)

#-------------------------------------------------------------------------------

# Iteration summary header
print "Iteration\tLost\tNotLost\tTotal"

for iteration in range(0,interations):
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

	#--------------------
	# Simulate PLS prime
	#--------------------
	for i in range(0, feature_count_1):
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

	#---------------------------
	# Simulate current wetlands
	#---------------------------

	# Simulate WWI ortho prime
	fid,wwi_prime = simulate_poly(feature_count_2,wwi_ortho_layer,wwi_ortho_accuracy,wwi_prime_def,0,wwi_prime)

	# Simulate WWI nonortho prime
	fid,wwi_prime = simulate_poly(feature_count_3,wwi_nonortho_layer,wwi_nonortho_accuracy,wwi_prime_def,fid,wwi_prime)

	# Simulate NWI La Crosse prime
	fid,wwi_prime = simulate_poly(feature_count_4,nwi_lacrosse_layer,nwi_lacrosse_accuracy,wwi_prime_def,fid,wwi_prime)

	# Simulate NWI Others prime
	fid,wwi_prime = simulate_poly(feature_count_5,nwi_others_layer,nwi_others_accuracy,wwi_prime_def,fid,wwi_prime)

	# End introduce error ----------------------------------------------------------

	#---------------------------------
	# PLS within/outside WWI wetlands
	#---------------------------------
	TrueCount = 0
	FalseCount = 0

	# Set ouput csv file
	csv_path = os.path.join(path, "output/results_"+str(iteration)+".csv")
	csv_out = open(csv_path,"a")

	# Iterate through point features to find where points intersect WWI
	for i in range(0, feature_count_1):  # For each PLS feature
		for j in range(0, wwi_prime.GetFeatureCount()):  # Check each current wetland poly until one is found to overlap
			# Get PLS feature and set geom refs
			point_feature = pls_prime.GetFeature(i)
			point = point_feature.GetGeometryRef()
			wwi_prime_feature = wwi_prime.GetFeature(j)
			poly = wwi_prime_feature.GetGeometryRef()

			# Check if WWI intersects PLS point
			cross = poly.Intersects(point)

			# Count the number of intersects or nots
			if cross:
				TrueCount = TrueCount + 1
				# Add line to csv
				csv_out.write(str(point_feature.GetField("CORN_ID"))[:11]+",1,"+str(iteration)+"\n")
				break  # Once at least one current wetland is found to overlap the historical wetland point, we need not keep searching
				
	# Iteration summary
	print str(iteration)+"\t"+str(TrueCount)+"\t"+str(feature_count_1-TrueCount)+"\t"+str(feature_count_1)

	# Close csv
	csv_out.close()

	# Remove temp directory
	shutil.rmtree(temp_dir)

	# Free memory
	pls_prime_dst = None
	pls_prime = None
	wwi_prime_dst = None
	wwi_prime = None

t1 = time.clock()
print "Time to complete:",t1-t0

# Free memory
wwi_ortho_source = None
wwi_ortho_layer = None
wwi_nonortho_source = None
wwi_nonortho_layer = None
nwi_lacrosse_source = None
nwi_lacrosse_layer = None
nwi_others_source = None
nwi_others_layer = None
pls_source = None
pls_layer = None