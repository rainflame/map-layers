import subprocess
import sqlite3
import pyproj
import re

mbtiles_file = "data/rgb.mbtiles"

# Run gdalinfo to get corner coordinates
gdalinfo_output = subprocess.check_output(["gdalinfo", mbtiles_file]).decode()


pattern = re.compile(r"\((.*?)\)")
matches = [
    pattern.search(line).group(1).split(",")
    for line in gdalinfo_output.splitlines()
    if line.startswith(("Upper Left", "Lower Left", "Upper Right", "Lower Right"))
]

# trim the whitespace and convert to floats
matches = [[coord.strip() for coord in match] for match in matches]

upper_left = matches[0]
lower_left = matches[1]
upper_right = matches[2]
lower_right = matches[3]

# Create coordinate transformation
transformer = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

# Convert projected coordinates to lat/lon
upper_left_lon, upper_left_lat = transformer.transform(upper_left[0], upper_left[1])
lower_right_lon, lower_right_lat = transformer.transform(lower_right[0], lower_right[1])

bounds = f"{upper_left_lon},{lower_right_lat},{lower_right_lon},{upper_left_lat}"

print("adding bounds {}".format(bounds))

# Open the database
connection = sqlite3.connect(mbtiles_file)
cursor = connection.cursor()

# Check if the 'bounds' metadata already exists
cursor.execute("SELECT * FROM metadata WHERE name=?", ("bounds",))
existing_bounds = cursor.fetchone()

if existing_bounds:
    # Update the existing 'bounds' metadata
    cursor.execute("UPDATE metadata SET value=? WHERE name=?", (bounds, "bounds"))
else:
    # Insert new 'bounds' metadata
    cursor.execute(
        "INSERT INTO metadata (name, value) VALUES (?, ?)", ("bounds", bounds)
    )


# Commit the changes and close the connection
connection.commit()
connection.close()
