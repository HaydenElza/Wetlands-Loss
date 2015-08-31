# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# simplify.py
# Created on: 2015-07-30 19:25:17.00000
#   (generated by ArcGIS/ModelBuilder)
# Description: 
# ---------------------------------------------------------------------------

# Set the necessary product code
import arceditor


# Import arcpy module
import arcpy


# Local variables:
wwi_ortho_shp = "E:\\Hayden_Elza\\temp4\\wwi_ortho.shp"
wwi_ortho_simp1_0_shp = "E:\\Hayden_Elza\\temp4\\wwi_ortho_simp1.shp"
tolerance = "1"

# Process: Simplify Polygon
arcpy.SimplifyPolygon_cartography(wwi_ortho_shp, wwi_ortho_simp1_0_shp, "POINT_REMOVE", tolerance, "0 Unknown", "RESOLVE_ERRORS", "NO_KEEP")

