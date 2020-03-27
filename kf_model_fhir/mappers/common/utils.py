def make_select(eng, table, *args):
    row = next(eng.execute(f'SELECT * FROM {table};'))
    cols = set(a for a in args) & set(row.keys())
    colstr = '"' + '","'.join(cols) + '"'
    yield from eng.execute(f'SELECT DISTINCT {colstr} FROM {table};')

def get(row, col):
    res = dict(row).get(col)
    return None if res == '' else res