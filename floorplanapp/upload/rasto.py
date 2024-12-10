import os
import requests
import json
from django.conf import settings
import warnings
from gradio_client import Client, handle_file

def fetch(filename):
    print("[SERVER] Detecting Edges", os.path.join(settings.MEDIA_ROOT, filename))
    client = Client("RasterScan/Automated-Floor-Plan-Digitalization")
    r = client.predict(
            file=handle_file(os.path.join(settings.MEDIA_ROOT, filename)),
            api_name="/run"
    )

    print("[SERVER] Generating 3D model")
    json_data = r[1]
    out_file = open("scans/myfile.json", "w")
    json.dump(json_data, out_file, indent = 6)
    out_file.close()

    os.system("cd ..\\blender && blender -b -P ..\\floorplanapp\\upload\\3dfily.py")