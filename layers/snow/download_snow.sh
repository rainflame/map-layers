# create a temp dir 

# download from https://noaadata.apps.nsidc.org/NOAA/G02158/masked/2023/11_Nov/SNODAS_20231108.tar
# https://noaadata.apps.nsidc.org/NOAA/G02158/masked/[year]/[day]_[month_abbreviation]/SNODAS_[yearmonthday].tar

# untar the directory

# enter the directory 

# unzip *.gz

# find the last file (TODO: figure out the naming convention)

# create a new file with the same filename.hdr containing: 
ENVI
samples = 6935
lines = 3351
bands = 1
header offset = 0
file type = ENVI Standard
data type = 2
interleave = bsq
byte order = 1

# convert to GEOtiff
gdal_translate -of GTiff -a_srs '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs' -a_nodata -9999 -a_ullr -124.73375000000000 52.87458333333333 -66.94208333333333 24.94958333333333 <input.dat> <output.tif>

# mask the geotiff to the bounding box

# create contours (step -10?) based on the pixel values (0 -> -9999)

# run the vectorization aglorithm on the raster 

# tile the vectorized contours to pmtiles 

# upload to r2 

# delete the temp dir 




