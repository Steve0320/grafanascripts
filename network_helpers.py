import json


# Extract values from JSON
def find_values(keys, jstr):

    results = []

    def _decode_dict(a_dict):
        for key in keys:
            try:
                results.append(a_dict[key])
            except KeyError:
                pass
        return a_dict

    json.loads(jstr, object_hook=_decode_dict)  # Return value ignored.
    return results