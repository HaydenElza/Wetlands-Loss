# ------------------------------------------------------------------------------------------------
# Script name: data_prep.py
# Created on: July 17, 2015
# Author: Hayden Elza
# Purpose: This script is used to prepare the NWI and WWI data for analysis. It first repairs the 
#			geometry, then "integrates" to remove slivers between polygons, then the features are
#			dissolved to reduce the number of vertices to simulate, lastly the geometries are
#			simplified using the Douglas-Pauker method to reduce cases of small inter-vertex 
#			distance.
# Version: 1.0
# History:
# -------------------------------------------------------------------------------------------------

import arcpy

