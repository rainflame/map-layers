import os
import requests
import urllib3
from alive_progress import alive_bar


# using the 1 arc-second dataset, but could use 1/3 arc-second for higher resolution
dataset = "National Elevation Dataset (NED) 1 arc-second"

# set the bounding box for the region we want to download DEMs for
us_continental_bbox = "-125.0011,24.9493,-66.9326,49.5904"
# us_west_bbox = "-100.336147,50.059513,-127.850165,29.983312"
# oregon_bbox = "-124.566244,46.864746,-116.463504,41.991794"

# USGS national map api endpoint to list DEMs for our bounding box
url = "https://tnmaccess.nationalmap.gov/api/v1/products?datasets={}&bbox={}".format(
    dataset, us_continental_bbox
)

response = requests.get(url)
data = response.json()

urls = []
download_bytes = 0

total_items = data["total"]
n = len(data["items"])

with alive_bar(
    int(total_items / 50),  # 50 items per page
    title="Getting list of tile URLs in bounding box region...",
    force_tty=True,
) as bar:
    while n < total_items:
        url += "&offset=" + str(n)
        response = requests.get(url + "&offset={}".format(n))
        data = response.json()
        for item in data["items"]:
            urls.append(item["downloadURL"])
            download_bytes += item["sizeInBytes"]

        n += len(data["items"])
        bar()


print("Approximate total download size: {:.2f} GB".format(download_bytes / 1e9))


# create data/sources/ dir if it doesn't already exist
if not os.path.exists("data/sources"):
    os.makedirs("data/sources")

# filter out any urls that already exist as saved files
filtered_urls = [
    url
    for url in urls
    if not os.path.exists(os.path.join("data/sources", url.split("/")[-1]))
]

print(
    "Skipping downloading {} files that already exist".format(
        len(urls) - len(filtered_urls)
    )
)


def request(method, url):
    try:
        r = urllib3.request(method, url)
        return r
    except Exception as e:
        print("Failed to download", url, e)
        return None


# download the data and save each file to data/sources/
with alive_bar(len(filtered_urls), title="Downloading data...", force_tty=True) as bar:
    for url in filtered_urls:
        filename = url.split("/")[-1]
        try:
            filepath = os.path.join("data/sources", filename)
            if not os.path.exists(filepath):
                data = request("GET", url)
                # save the data to filepath
                with open(filepath, "wb") as f:
                    f.write(data.data)
        except Exception as e:
            print("Failed to save file", filename, e)
        bar()
