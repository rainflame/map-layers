from tqdm import tqdm

from loop import Loop

    
def build(covers):
    all_loops = []
    loop_count = 0

    for c in tqdm(range(len(covers)), desc="Building loops"):
        cover = covers[c]

        exterior = Loop(loop_count, cover.polygon.exterior)
        loop_count += 1

        interiors = [Loop(loop_count + i, l) for i, l in enumerate(cover.polygon.interiors)]
        loop_count += len(cover.polygon.interiors)

        cover.exterior = exterior
        cover.interiors = interiors

        all_loops.extend([exterior] + interiors)

    return all_loops

def rebuild(loops):
    for l in tqdm(range(len(loops)), desc="Rebuilding loops"):
        loop = loops[l]
        loop.rebuild()