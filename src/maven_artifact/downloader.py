import hashlib
import os
from .requestor import Requestor, RequestException
from .resolver import Resolver
from .artifact import Artifact
import sys
import getopt


class Downloader(object):
    def __init__(self, base="http://repo1.maven.org/maven2", username=None, password=None):
        self.requestor = Requestor(username, password)
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


__doc__ = """
   Usage:
   %(program_name)s <options> Maven-Coordinate filename
   Options:
     -m <url>       --maven-repo=<url>
     -u <username>  --username=<username>
     -p <password>  --password=<password>
     -ht <hashtype> --hash-type=<hashtype>

   Maven-Coordinate are defined by: http://maven.apache.org/pom.html#Maven_Coordinates
      The possible options are:
      - groupId:artifactId:version
      - groupId:artifactId:packaging:version
      - groupId:artifactId:packaging:classifier:version
    filename is optional. If not supplied the filename will be <artifactId>.<extension>
    The filename directory must exist prior to download.

   Example:
     %(program_name)s "org.apache.solr:solr:war:3.5.0"
  """


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "m:u:p:ht", ["maven-repo=", "username=", "password=", "hash-type="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    if not len(args):
        print("No maven coordiantes supplied")
        usage()
        sys.exit(2)
    else:
        options = dict(opts)

        base = options.get("-m") or options.get("--maven-repo", "https://repo1.maven.org/maven2")
        username = options.get("-u") or options.get("--username")
        password = options.get("-p") or options.get("--password")
        hash_type = options.get("-ht") or options.get("--hash-type", "md5")

        dl = Downloader(base, username, password)

        artifact = Artifact.parse(args[0])

        filename = args[1] if len(args) == 2 else None

        try:
            if dl.download(artifact, filename, hash_type):
                sys.exit(0)
            else:
                usage()
                sys.exit(1)
        except RequestException as e:
            print(e.msg)
            sys.exit(1)


def usage():
    print(__doc__ % {"program_name": os.path.basename(sys.argv[0])})


if __name__ == "__main__":
    main()
