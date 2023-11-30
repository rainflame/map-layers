#!/bin/bash

# echo -e "\nFiltering out overlapping contours...\n"

# ogr2ogr -f "GeoJSONSeq" \
#             -sql "SELECT * FROM \"contour_200\" WHERE elevation % 1000 != 0" \
#             "data/temp/200/contour_200_filtered.geojsons" \
#             "data/temp/200/contour_200.geojsons" \
#             -progress

# ogr2ogr -f "GeoJSONSeq" \
#             -sql "SELECT * FROM \"contour_40\" WHERE elevation % 1000 != 0" \
#             "data/temp/40/contour_40_filtered.geojsons" \
#             "data/temp/40/contour_40.geojsons" \
#             -progress


# echo -e "\nTiling dataset...\n"

# # tile contours, creating three separate files with 40ft, 200ft, and 1000ft contours at different zoom levels
# tippecanoe -Z10 -z16 -P -y elevation -l contour_1000 \
#     data/temp/1000/contour_1000.geojsons --read-parallel \
#     --drop-densest-as-needed \
#     --simplification=5 \
#     --hilbert \
#     --visvalingam \
#     -o data/temp/contour_1000.mbtiles \
#     --force

tippecanoe -Z11 -z16 -P -y elevation -l contour_200 \
    data/temp/200/contour_200_filtered.geojsons --read-parallel \
    --drop-densest-as-needed \
    --simplification=5 \
    --hilbert \
    --visvalingam \
    -o data/temp/contour_200.mbtiles \
    --force

tippecanoe -Z12 -z16 -P -y elevation -l contour_40 \
    data/temp/40/contour_40_filtered.geojsons --read-parallel \
    --drop-densest-as-needed \
    --simplification=5 \
    --hilbert \
    --visvalingam \
    -o data/temp/contour_40.mbtiles \
    --force

echo -e "\nMerging layers...\n"

tile-join -o data/output/contours.mbtiles data/temp/contour_1000.mbtiles data/temp/contour_200.mbtiles data/temp/contour_40.mbtiles --force

echo -e "\n\nDone, created:\ndata/output/contours.mbtiles\n"
