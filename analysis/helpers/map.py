def add_keys(first: dict[object, int], second: dict[object, int]):
    r = {}
    for k,v in first.items():
        r[k] = first[k] + second[k]

    for k,v in second.items():
        if k not in first:
            raise Exception(f"Failed to add keys as maps are not the same first: {first.keys()} second: {second.keys()}")

    return r