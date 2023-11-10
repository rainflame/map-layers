# create a temp dir 
mkdir -p /tmp/snow/

# Get the current year, month, and day
current_date=$(date +'%Y%m%d')
year=${current_date:0:4}
month=${current_date:4:2}
day=${current_date:6:2}
month_abbreviation=$(date +'%b')

# download from https://noaadata.apps.nsidc.org/NOAA/G02158/masked/2023/11_Nov/SNODAS_20231108.tar
wget -P /tmp/snow/ -O data.tar "https://noaadata.apps.nsidc.org/NOAA/G02158/masked/${year}]/${day}_${month_abbreviation}/SNODAS_${year}${month}${day}].tar"
tar -xvf /tmp/snow/data.tar -C /tmp/snow/
gunzip /tmp/snow/*.gz

# see https://nsidc.org/sites/default/files/g02158-v001-userguide_2_1.pdf for naming convention
# region: US
# model: SSMV
# type: snow model output
# product: snow depth
# data: integral through the snowpack
# time: 1 hour snapshot 
# us_ssmv11036tS__T0001TTNATSyyyymmddhhIP00Z.xxx.gz

# 2023 11 09 05 H P001
files=$(ls us_ssmv11036tS__T0001TTNATS*.gz)

if [ -z "$files" ]; then
    echo "No snowcover file with correct type found"
    exit 1
fi

# select the last file (latest)
if [ -n "$files" ]; then
    last_file=$(echo $files | awk '{print $NF}')
    echo $last_file
fi






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




