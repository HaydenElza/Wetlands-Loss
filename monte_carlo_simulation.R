# Load packages
  install.packages("rgdal")
  library("rgdal")
  install.packages("maptools")
  library("maptools")
  install.packages("rgeos")
  library("rgeos")
  install.packages("raster")
  library("raster")


# Set working directory
  setwd("e:/Hayden_Elza/Wetlands-Loss/data/")
  
# Read in shapefiles for current and historical wetlands
  historical_wetlands <- readOGR(getwd(), "PLS_Analysis3")
  current_wetlands <- readOGR(getwd(), "WWI_Analysis3")
  
# Introduce random error within dataset's spatial accuracy
  
# Select by location: within/outside
  
# Break up data according to enumeration units: North/South Ecoregions, per County
  
# Point Sampling
  
# Export summary tables