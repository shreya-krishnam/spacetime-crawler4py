import requests
import cbor
import time

from utils.response import Response

def download(url, config, logger=None):
    print(url)
    host, port = config.cache_server
    resp = requests.get(
        f"http://{host}:{port}/",
        params=[("q", f"{url}"), ("u", f"{config.user_agent}")])
    if resp:
       try:
          return Response(cbor.loads(resp.content))
       except EOFError:
          logger.error(f"EOF error {resp} with url {url}.")
    logger.error(f"Spacetime Response error {resp} with url {url}.")
    return Response({
        "error": f"Spacetime Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})
