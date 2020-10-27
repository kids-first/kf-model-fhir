import re


def join(*args):
    return "|".join(str(a) for a in args)


# http://hl7.org/fhir/R4/datatypes.html#id
def make_safe_identifier(target_id):
    if target_id is None:
        return None
    return re.sub(r"[^A-Za-z0-9\-\.]", "-", target_id)[:64]
