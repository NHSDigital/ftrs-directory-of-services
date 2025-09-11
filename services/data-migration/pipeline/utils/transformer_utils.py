# TODO: remove this logic and replace with ServiceValidator when merged
def extract_organisation_public_name(publicname: str) -> str:
    """
    Clean the public name by extracting the part before the first hyphen.
    """
    if publicname:
        return publicname.split("-", maxsplit=1)[0].rstrip()
    raise ValueError("publicname is not set")
