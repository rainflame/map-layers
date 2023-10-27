# create medial axes from the input polygons

import click
import os
import multiprocessing

import networkx as nx
import geojson

import skgeom as sg
from shapely.geometry import Polygon, LineString

from tqdm import tqdm


def load_geojson_geometries(input_file):
    with open(input_file) as f:
        gj = geojson.load(f)

    geometries = []
    for feature in gj["features"]:
        if feature["geometry"]["type"] != "Polygon":
            continue

        geom = Polygon(feature["geometry"]["coordinates"][0])
        geometries.append((geom, feature["properties"]))

    crs = gj["crs"]

    return geometries, crs


def dfs_longest_path(graph, start, visited, current_path):
    visited[start] = True
    current_path.append(start)

    longest_path = current_path.copy()

    for neighbor in graph.neighbors(start):
        if not visited[neighbor]:
            new_path = dfs_longest_path(graph, neighbor, visited, current_path)
            if len(new_path) > len(longest_path):
                longest_path = new_path

    current_path.pop()
    visited[start] = False

    return longest_path


def find_longest_path(graph):
    longest_path = []
    visited = {node: False for node in graph.nodes}

    for node in graph.nodes:
        if not visited[node]:
            current_path = dfs_longest_path(graph, node, visited, [])
            if len(current_path) > len(longest_path):
                longest_path = current_path

    return longest_path


def get_medial_axis(polygon):
    geom, properties = polygon
    # need to flip the coordinates for skgeom
    polygon = sg.Polygon([(y, x) for x, y, _ in geom.exterior.coords])
    # simplify the geometry to speed up the medial axis calculation
    polygon = sg.simplify(polygon, 0.5)
    skeleton = sg.skeleton.create_interior_straight_skeleton(polygon)

    graph = nx.Graph()

    for h in skeleton.halfedges:
        if h.is_bisector:
            p1 = h.vertex.point
            p2 = h.opposite.vertex.point
            # need to re-flip the coordinates
            graph.add_edge(
                (float(p1.y()), float(p1.x())), (float(p2.y()), float(p2.x()))
            )

    longest_path = find_longest_path(graph)

    # create a line from the longest path
    lines = []
    for i in range(len(longest_path) - 1):
        lines.append(LineString([longest_path[i], longest_path[i + 1]]))

    # join the lines into one
    joined_line = LineString()
    for line in lines:
        joined_line = joined_line.union(line)

    # simplify it a bit
    joined_line = joined_line.simplify(0.1, preserve_topology=False)
    return (joined_line, properties)


@click.command()
@click.option(
    "--workers", default=multiprocessing.cpu_count(), help="Number of workers to use"
)
@click.option(
    "--input-file",
    help="The input geojson",
    required=True,
)
@click.option(
    "--output-file",
    help="The output geojson",
    required=True,
)
def cli(workers, input_file, output_file):
    # check input exists
    if not os.path.exists(input_file):
        raise Exception(f"Cannot open {input_file}")

    # check path to output exists
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    geoms, crs = load_geojson_geometries(input_file)

    lines = []
    with multiprocessing.Pool(workers) as p:
        for line, properties in tqdm(
            p.imap_unordered(get_medial_axis, geoms), total=len(geoms)
        ):
            line = geojson.Feature(geometry=line, properties=properties)
            lines.append(line)
        p.close()
        p.join()

    with open(output_file, "w") as f:
        gj = geojson.FeatureCollection(lines, crs=crs)
        geojson.dump(gj, f)


if __name__ == "__main__":
    cli()
