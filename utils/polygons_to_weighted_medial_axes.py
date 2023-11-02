import click
import os
import multiprocessing

import networkx as nx
import geojson

import skgeom as sg
from shapely.geometry import Polygon, LineString, Point

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


def dfs_sum_weights(node_weights, graph, node, visited):
    node_point = Point(node)
    visited.add(node)

    neighbors = graph.neighbors(node)
    unvisited_neighbors = [n for n in neighbors if n not in visited]

    total = 0
    for n in unvisited_neighbors:
        n_point = Point(n)
        distance = n_point.distance(node_point)
        total += dfs_sum_weights(node_weights, graph, n, visited) + distance

    node_weights[node] = total
    return total


def get_heaviest_path(graph, node_weights, node, visited):
    visited.add(node)

    neighbors = graph.neighbors(node)
    unvisited_neighbors = [n for n in neighbors if n not in visited]

    # find unvisited neighbor with max node weight
    max_weight = 0
    max_weight_node = None
    for n in unvisited_neighbors:
        if node_weights[n] > max_weight:
            max_weight = node_weights[n]
            max_weight_node = n

    if max_weight_node is None:
        return [node]

    # recurse, and return given list and the element containing current node
    return get_heaviest_path(graph, node_weights, max_weight_node, visited) + [node]


# create an approximation of medial axes from the input polygons
# first, we create a skeleton of each polygon
# then, we find the weight of each node, which is the sum of the distance to all child nodes
# then, we find the two heaviest paths from the center node. this gives us the path from the cetner
# that is the furthest from the polygon boundary, an approxmiation for the most visually massive section of the polygon
# then, we join the two paths together to get the medial axis
def get_weighted_medial_axis(polygon):
    geom, properties = polygon
    try:
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

        # get the center of the graph
        center = nx.center(graph)[0]

        node_weights = {}
        dfs_sum_weights(node_weights, graph, center, set())

        neighbors = graph.neighbors(center)

        # get the two neighbors with the highest weights
        neighbor_weights = [(n, node_weights[n]) for n in neighbors]
        neighbor_weights.sort(key=lambda x: x[1], reverse=True)

        # get the two heaviest paths
        heaviest_paths = []
        for n, _ in neighbor_weights[:2]:
            heaviest_paths.append(
                get_heaviest_path(graph, node_weights, n, set([center]))
            )

        joined_line = LineString(heaviest_paths[0] + [center] + heaviest_paths[1][::-1])
        return (joined_line, properties)
    except Exception as e:
        print(e)
        print(f"Error processing polygon with properties: {properties}")
        print("Skipped polygon")
        return (None, properties)


def weighted_medial_axes_from_geojson(input_file, output_file, workers):
    # check input exists
    if not os.path.exists(input_file):
        raise Exception(f"Cannot open {input_file}")

    # check path to output exists
    output_dir = os.path.dirname(output_file)
    if output_dir != "" and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    geoms, crs = load_geojson_geometries(input_file)

    lines = []
    with multiprocessing.Pool(workers) as p:
        for line, properties in tqdm(
            p.imap_unordered(get_weighted_medial_axis, geoms), total=len(geoms)
        ):
            if line is None:
                continue
            line = geojson.Feature(geometry=line, properties=properties)
            lines.append(line)
        p.close()
        p.join()

    with open(output_file, "w") as f:
        gj = geojson.FeatureCollection(lines, crs=crs)
        geojson.dump(gj, f)


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
    weighted_medial_axes_from_geojson(input_file, output_file, workers)


if __name__ == "__main__":
    cli()
