def get(row, col):
    res = row.get(col)
    return None if res == "" else res


def coding(x, systems, name):
    def list_codings(x, systems, name):
        results = [s[x] for s in systems if x in s]
        if not results:
            raise Exception(f"No {name} codings found for {x}")
        return results
        
    return {
        "coding": list_codings(x, systems, name),
        "text": x
    }
