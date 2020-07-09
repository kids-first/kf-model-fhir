import re


def join(*args):
    return "|".join(str(a) for a in args)


# http://hl7.org/fhir/R4/datatypes.html#id
def make_identifier(*args):
    return re.sub(r"[^A-Za-z0-9\-\.]", "-", ".".join(str(a) for a in args))[:64]
