import arcpy, arceditor, multiprocessing
from sys import argv

input_shp = argv[1]
output_dir = argv[2]
tolerance = argv[3]
output_shp = output_dir+"simp.shp"
merge_list = []

def simplify(fid_range):
	# Build file names
	input_shp_select = output_dir+"_"+str(fid_range[0])+"_temp.shp"
	output_shp_select = output_dir+"_"+str(fid_range[0])+".shp"

	# Add file name to merge list and build select querry
	merge_list.append(output_shp_select)
	where = '"FID" > '+str(fid_range[0])+' AND "FID" < '+str(fid_range[1])

	# Select and Simplify
	print "Selecting >>> FID:",fid_range[0]
	arcpy.Select_analysis(input_shp, input_shp_select, where)
	print "Simplifying >>> FID:",fid_range[0]
	arcpy.SimplifyPolygon_cartography(input_shp_select, output_shp_select, "POINT_REMOVE", tolerance, "0 Unknown", "RESOLVE_ERRORS", "NO_KEEP")
	print "Finished >>> FID:",fid_range[0]

def main():
	print "Started..."

	# Create list of twelve ranges of features
	feature_count = int(arcpy.GetCount_management(input_shp).getOutput(0))
	range_len = feature_count/12
	fid_range = [[0, range_len], [range_len+1, 2*range_len], [2*range_len+1, 3*range_len], [3*range_len+1, 4*range_len], [4*range_len+1, 5*range_len], [5*range_len+1, 6*range_len], [6*range_len+1, 7*range_len], [7*range_len+1, 8*range_len], [8*range_len+1, 9*range_len], [9*range_len+1, 10*range_len], [10*range_len+1, 11*range_len], [11*range_len+1, feature_count]]
	
	arcpy.env.overwriteOutput = True

	# Create a pool class and run the jobs
	pool = multiprocessing.Pool(12)
	pool.map(simplify,fid_range)

	# Synchronize the main process with the job processes to ensure proper cleanup.
	pool.close()
	pool.join()

	# Merge all threads
	print "Merging... merge_list:",merge_list
	arcpy.Merge_management([merge_list[0],merge_list[1],merge_list[2],merge_list[3],merge_list[4],merge_list[5],merge_list[6],merge_list[7],merge_list[8],merge_list[9],merge_list[10],merge_list[11]],output_shp)

if __name__ == "__main__":
	main()