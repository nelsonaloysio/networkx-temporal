from os import environ

NX_GPU_AUTOCONFIG = environ.get("NX_GPU_AUTOCONFIG", "0").lower() in ("1", "true")
NX_CUGRAPH_AUTOCONFIG = environ.get("NX_CUGRAPH_AUTOCONFIG", "0").lower() in ("1", "true")
