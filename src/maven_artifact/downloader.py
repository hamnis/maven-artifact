import hashlib
import os

from maven_artifact.requestor import RequestException, Requestor
from maven_artifact.resolver import Resolver


class Downloader:
    def __init__(self, base="https://repo.maven.apache.org/maven2", username=None, password=None, token=None):
        self.requestor = Requestor(username=username, password=password, token=token)
        self.resolver = Resolver(base, self.requestor)

    def download(self, artifact, filename=None, hash_type="md5"):
        filename = artifact.get_filename(filename)
        url = self.resolver.uri_for_artifact(artifact)
        if os.path.exists(filename) and self.verify_file(filename, url, hash_type=hash_type):
            print("%s is already up to date" % artifact)
            return artifact

        print(f"Downloading artifact {artifact} from {url}")

        def onError(uri, err):
            self._throwDownloadFailed(f"Failed to download {artifact} from {uri} \n{err}")

        with self.requestor.request(url, onError, stream=True) as r:
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Maven artifact {artifact} is downloaded to {filename}")
        return artifact

    def _throwDownloadFailed(self, msg):
        raise RequestException(msg)

    def verify_file(self, file, url, hash_type: str = "md5"):
        url = f"{url}.{hash_type}"

        def onError(uri, err):
            self._throwDownloadFailed("Failed to download hash file from " + uri)

        remote_hash = self.requestor.request(url, onError, lambda r: r.text)
        local_hash = getattr(hashlib, hash_type)(open(file, "rb").read()).hexdigest()
        return remote_hash == local_hash
