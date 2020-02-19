import re

def get(row, col):
    res = dict(row).get(col)
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


def make_identifier(*args):
    return re.sub(
        r"[^A-Za-z0-9\-\.]",
        "-",
        ".".join(str(a) for a in args)
    )


def make_select(eng, table, *args):
    row = next(eng.execute(f"SELECT * FROM {table};"))
    cols = set(a for a in args) & set(row.keys())
    colstr = '"' + '","'.join(cols) + '"'
    yield from eng.execute(f"SELECT DISTINCT {colstr} FROM {table};")
