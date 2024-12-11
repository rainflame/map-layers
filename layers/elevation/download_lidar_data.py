import requests
import re
import tqdm


url = "https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/dem/OLC_Deschutes_DEM_2009-2011_7382/"

# index contains all the links to tifs
response = requests.get(url + "index.html")

# extract every link with a .tif extension
links = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)
links = [link for link in links if link.endswith(".tif")]

print(f"Downloading {len(links[:5])} files...")
for link in tqdm.tqdm(links[:5]):
    response = requests.get(url + link)
    filename = link.split("/")[-1]
    file_path = f"data/sources/{filename}"
    with open(file_path, "wb") as f:
        f.write(response.content)
