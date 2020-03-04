import re

GO_AWAY_SERVER = "<div xmlns=\"http://www.w3.org/1999/xhtml\"></div>"


def get(row, col):
    res = dict(row).get(col)
    return None if res == "" else res


def codeable_concept(x, systems, name):
    def list_codings(x, systems, name):
        results = [s[x] for s in systems if x in s]
        if not results:
            raise Exception(f"No {name} codings found for {x}")
        return results
        
    return {
        "coding": list_codings(x, systems, name),
        "text": x
    }


# http://hl7.org/fhir/R4/datatypes.html#id
def make_identifier(*args):
    return re.sub(
        r"[^A-Za-z0-9\-\.]",
        "-",
        ".".join(str(a) for a in args)
    )[:64]


def make_select(eng, table, *args):
    row = next(eng.execute(f"SELECT * FROM {table};"))
    cols = set(a for a in args) & set(row.keys())
    colstr = '"' + '","'.join(cols) + '"'
    yield from eng.execute(f"SELECT DISTINCT {colstr} FROM {table};")
