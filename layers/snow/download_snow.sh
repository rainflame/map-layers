#!/bin/bash

SOURCES=data/sources
OUTPUT=data/output

current_date=$1 # assumes format '%Y%m%d%b'

# Get the current year, month, and day
year=${current_date:0:4}
month=${current_date:4:2}
day=${current_date:6:2}
month_abbreviation=${current_date:8:3}

echo -e "\nDownloading snow data for $year-$month-$day...\n"
echo "https://noaadata.apps.nsidc.org/NOAA/G02158/unmasked/${year}/${month}_${month_abbreviation}/SNODAS_unmasked_${year}${month}${day}.tar"

# url format like https://noaadata.apps.nsidc.org/NOAA/G02158/unmasked/2023/11_Nov/SNODAS_unmasked_20231108.tar
curl -o $SOURCES/data.tar "https://noaadata.apps.nsidc.org/NOAA/G02158/unmasked/${year}/${month}_${month_abbreviation}/SNODAS_unmasked_${year}${month}${day}.tar" --progress-bar

echo -e "\nExtracting...\n"

tar -xvf $SOURCES/data.tar -C $SOURCES/
gunzip $SOURCES/*.gz

# see https://nsidc.org/sites/default/files/g02158-v001-userguide_2_1.pdf for naming convention
# region: US
# model: SSMV
# type: snow model output
# product: snow depth
# data: integral through the snowpack
# time: 1 hour snapshot 
# us_ssmv11036tS__T0001TTNATSyyyymmddhhIP00Z.dat
files=$(ls $SOURCES/zz_ssmv11036tS__T0001TTNATS*.dat)

if [ -z "$files" ]; then
    echo "No snowcover file with correct type found"
    exit 1
fi

# select the last file (latest if there are multiple)
if [ -n "$files" ]; then
    last_file=$(echo "$files" | awk '{print $NF}')
    echo "$last_file"
fi

filename=$(echo "$last_file" | cut -f 1 -d '.')

# get the date and time from the yyyymmddhhHP001 portion of the filename
parsed_year="${filename: -15:4}"
parsed_month="${filename: -11:2}"
parsed_day="${filename: -9:2}"
parsed_hour="${filename: -7:2}"

# save parsed date and time to a json file 
echo "{\"year\": \"$parsed_year\", \"month\": \"$parsed_month\", \"day\": \"$parsed_day\", \"hour\": \"$parsed_hour\"}" > $OUTPUT/snow-meta.json

# create filename.hdr file
# https://nsidc.org/data/user-resources/help-center/how-do-i-convert-snodas-binary-files-geotiff-or-netcdf
echo "ENVI
samples = 8192
lines = 4096
bands = 1
header offset = 0
file type = ENVI Standard
data type = 2
interleave = bsq
byte order = 1
" > "$filename".hdr

echo -e "\nConverting to GeoTIFF format...\n"

# convert to GEOtiff
gdal_translate -of GTiff -a_srs '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs' \
            -a_nodata -9999 -a_ullr \
            -130.51666666666667 \
            58.23333333333333 \
            -62.25000000000000 \
            24.10000000000000 \
            "$last_file" $SOURCES/snow-conus.tif

# clean up the sources directory
rm $SOURCES/*.dat
rm $SOURCES/*.txt
rm $SOURCES/*.tar
rm $SOURCES/*.hdr

echo -e "\nDone!\n"
