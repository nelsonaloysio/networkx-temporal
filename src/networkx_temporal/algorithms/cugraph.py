from os import environ

NX_CUGRAPH_AUTOCONFIG = False
if environ.get("NX_CUGRAPH_AUTOCONFIG", "0").lower() in ("1", "true"):
    NX_CUGRAPH_AUTOCONFIG = True
