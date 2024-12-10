import os
import requests
import urllib3
import click
import tqdm
import multiprocessing

# using the 1 arc-second dataset, but could use 1/3 arc-second for higher resolution
dataset = "National Elevation Dataset (NED) 1 arc-second"


# use urllib3 to download a url
def request(method, url):
    try:
        r = urllib3.request(method, url)
        return r
    except Exception as e:
        print("Failed to download", url, e)
        return None


# download a url to data/sources/
def download(url):
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


# click cli to get number of workers and bounding box
@click.command()
@click.option(
    "--workers", default=multiprocessing.cpu_count(), help="Number of workers to use"
)
@click.option("--dataset", default=dataset, help="Dataset to download data for")
@click.option(
    "--bbox",
    default="-124.566244,46.864746,-116.463504,41.991794",
    help="Bounding box to download data for",
)
def cli(workers, dataset, bbox):
    print("Getting region details from the National Map API...")
    # USGS national map api endpoint to list DEMs for our bounding box
    url = (
        "https://tnmaccess.nationalmap.gov/api/v1/products?datasets={}&bbox={}".format(
            dataset, bbox
        )
    )

    response = requests.get(url)
    data = response.json()

    urls = []
    download_bytes = 0

    total_items = data["total"]
    n = len(data["items"])
    for item in data["items"]:
        urls.append(item["downloadURL"])
        download_bytes += item["sizeInBytes"]

    print("Getting list of tile URLs in bounding box region...")
    with tqdm.tqdm(total=total_items) as pbar:
        pbar.update(n)
        while n < total_items:
            url += "&offset=" + str(n)
            response = requests.get(url + "&offset={}".format(n))
            data = response.json()
            for item in data["items"]:
                urls.append(item["downloadURL"])
                download_bytes += item["sizeInBytes"]

            n += len(data["items"])
            pbar.update(len(data["items"]))

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

    print("Downloading {} files...".format(len(filtered_urls)))

    # download the data in parallel save each file to data/sources/
    with multiprocessing.Pool(processes=workers) as pool:
        for _ in tqdm.tqdm(
            pool.imap_unordered(download, filtered_urls), total=len(filtered_urls)
        ):
            pass
        pool.close()
        pool.join()


if __name__ == "__main__":
    cli()
