Resources for python script:
- [Extract point from raster](http://pthelma.readthedocs.org/en/latest/dev/spatial.html#spatial.extract_point_from_raster)
	
	~~~ python
	def extract_point_from_raster(point, data_source, band_number=1):
	"""Return floating-point value that corresponds to given point."""

	# Convert point co-ordinates so that they are in same projection as raster
	point_sr = point.GetSpatialReference()
	raster_sr = osr.SpatialReference()
	raster_sr.ImportFromWkt(data_source.GetProjection())
	transform = osr.CoordinateTransformation(point_sr, raster_sr)
	point.Transform(transform)

	# Convert geographic co-ordinates to pixel co-ordinates
	x, y = point.GetX(), point.GetY()
	forward_transform = Affine.from_gdal(*data_source.GetGeoTransform())
	reverse_transform = ~forward_transform
	px, py = reverse_transform * (x, y)
	px, py = int(px + 0.5), int(py + 0.5)

	# Extract pixel value
	band = data_source.GetRasterBand(band_number)
	structval = band.ReadRaster(px, py, 1, 1, buf_type=gdal.GDT_Float32)
	result = struct.unpack('f', structval)[0]
	if result == band.GetNoDataValue():
		result = float('nan')
	return result
	~~~

- [Python – Extract raster data value at a point (*simple*)](https://waterprogramming.wordpress.com/2014/10/07/python-extract-raster-data-value-at-a-point/)
	
	~~~ python
	from __future__ import division
	from osgeo import gdal
	from geopy.geocoders import Nominatim
	 
	def get_value_at_point(rasterfile, pos):
	  gdata = gdal.Open(rasterfile)
	  gt = gdata.GetGeoTransform()
	  data = gdata.ReadAsArray().astype(np.float)
	  gdata = None
	  x = int((pos[0] - gt[0])/gt[1])
	  y = int((pos[1] - gt[3])/gt[5])
	  return data[y, x]
	 
	city = 'Ithaca, NY'
	g = Nominatim().geocode(city, timeout=5)
	p = (g.longitude,g.latitude)
	print get_value_at_point('path/to/my/raster/file', p)
	~~~

- 
