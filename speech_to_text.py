import requests
import tarfile
import tempfile

# Step 1: Determine the latest package
r = requests.get('https://registry.npmjs.org/microsoft-cognitiveservices-speech-sdk')
j = r.json()
latest_version = list(j['versions'].keys())[-1]
package_url = j['versions'][latest_version]['dist']['tarball']

# Step 2: Download and extract the latest javascript file
target_name = 'package/distrib/browser/microsoft.congnitiveservices.speech.sdk.bundle-min.js'
with tempfile.TemporaryFile() as f:
  with requests.get(package_url, stream=True) as r:
    for chunk in r.iter_content(chunk_size=8192):
      f.write(chunk)
      
  f.seek(0)
  tar = tarfile.open(f)
  tar.extractall([m for m in tar if m.name == target_name])
  tar.close()

# Step 3: 