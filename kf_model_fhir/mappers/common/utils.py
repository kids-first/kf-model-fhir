import re


# http://hl7.org/fhir/R4/datatypes.html#id
def make_identifier(*args):
    return re.sub(r"[^A-Za-z0-9\-\.]", "-", ".".join(str(a) for a in args))[:64]


def make_select(eng, table, *args):
    row = next(eng.execute(f"SELECT * FROM {table};"))
    cols = {a for a in args} & set(row.keys())
    colstr = '"' + '","'.join(cols) + '"'
    yield from eng.execute(f"SELECT DISTINCT {colstr} FROM {table};")


def get(row, col):
    res = dict(row).get(col)
    return None if res == "" else res
