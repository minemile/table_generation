def parse_location(location, x_margin=0, y_margin=0):
    x_min = int(location["x"]) - x_margin
    y_min = int(location["y"]) - y_margin
    x_max = x_min + int(location["width"])
    y_max = y_min + int(location["height"])
    return x_min, y_min, x_max, y_max
    
def bbox_to_4_coords(bbox):
    coords = []
    x_min, y_min, x_max, y_max = bbox
    x_left_down, y_left_down = x_min, y_max
    x_right_up, y_right_up = x_max, y_min
    coords.append(
        (
            x_min,
            y_min,
            x_right_up,
            y_right_up,
            x_max,
            y_max,
            x_left_down,
            y_left_down,
        )
    )
    return coords

def parse_locations(raw_locations):
    if len(raw_locations) == 0:
        return raw_locations
    bboxes = []
    x_margin = 0
    y_margin = 0
    # x_margin = min([elem["x"] for elem in raw_locations])
    # y_margin = min([elem["y"] for elem in raw_locations])

    for elem in raw_locations:
        parsed_location = parse_location(elem, x_margin, y_margin)
        bboxes.append(parsed_location)
    return bboxes