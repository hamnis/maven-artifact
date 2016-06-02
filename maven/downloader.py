import hashlib
import os
from requestor import Requestor,RequestException
from resolver import Resolver
from artifact import Artifact
import sys
import getopt

class Downloader(object):
    def __init__(self, base="http://repo1.maven.org/maven2", username=None, password=None):
        self.requestor = Requestor(username, password)
        self.resolver = Resolver(base, self.requestor)

    
    def download(self, artifact, filename=None, suppress_log=False):
        filename = artifact.get_filename(filename)
        url = self.resolver.uri_for_artifact(artifact)
        if not self.verify_md5(filename, url + ".md5"):
            if not suppress_log:
                print("Downloading artifact " + str(artifact))
                hook=self._chunk_report
            else:
                hook=self._chunk_report_suppress

            onError = lambda uri, err: self._throwDownloadFailed("Failed to download artifact " + str(artifact) + "from " + uri)
            response = self.requestor.request(url, onError, lambda r: r)
            
            if response:
                with open(filename, 'w') as f:
                    self._write_chunks(response, f, report_hook=hook)
                if not suppress_log:
                    print("Downloaded artifact %s to %s" % (artifact, filename))
                return (artifact, True)
            else:
                return (artifact, False)
        else:
            if not suppress_log:
                print("%s is already up to date" % artifact)
            return (artifact, True)

    def _throwDownloadFailed(self, msg):
        raise RequestException(msg)

    def _chunk_report_suppress(self, bytes_so_far, chunk_size, total_size):
        pass

    def _chunk_report(self, bytes_so_far, chunk_size, total_size):
        percent = float(bytes_so_far) / total_size
        percent = round(percent*100, 2)
        sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %
                 (bytes_so_far, total_size, percent))

        if bytes_so_far >= total_size:
            sys.stdout.write('\n')

    def _write_chunks(self, response, file, chunk_size=8192, report_hook=None):
        total_size = response.info().getheader('Content-Length').strip()
        total_size = int(total_size)
        bytes_so_far = 0

        while 1:
            chunk = response.read(chunk_size)
            bytes_so_far += len(chunk)

            if not chunk:
                break

            file.write(chunk)
            if report_hook:
                report_hook(bytes_so_far, chunk_size, total_size)

        return bytes_so_far

    def verify_md5(self, file, remote_md5):
        if not os.path.exists(file):
            return False
        else:
            local_md5 = self._local_md5(file)
            onError = lambda uri, err: _throwDownloadFailed("Failed to download MD5 from " + uri)
            remote = self.requestor.request(remote_md5, onError, lambda r: r.read())
            return local_md5 == remote

    def _local_md5(self, file):
        md5 = hashlib.md5()
        with open(file, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), ''):
                md5.update(chunk)
        return md5.hexdigest()


__doc__ = """
   Usage:
   %(program_name)s <options> Maven-Coordinate filename
   Options:
     -m <url>      --maven-repo=<url>
     -u <username> --username=<username>
     -p <password> --password=<password>
     
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
        opts, args = getopt.getopt(sys.argv[1:], "m:u:p:", ["maven-repo=", "username=", "password="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    if not len(args):
        print "No maven coordiantes supplied"
        usage()
        sys.exit(2)
    else:
        options = dict(opts)
        base = options.get("-m")
        if not base:
            base = options.get("--maven-repo")
        if not base:
            base = "https://repo1.maven.org/maven2"
        username = options.get("-u")
        if not username:
            username = options.get("--username")
        password = options.get("-p")
        if not password:
            options.get("--password")
        dl = Downloader(base, username, password)

        artifact = Artifact.parse(args[0])

        filename = None
        if len(args) == 2:
            filename = args[1]
        try:

            if dl.download(artifact, filename):
                sys.exit(0)
            else:
                usage()
                sys.exit(1)
        except RequestException, e:
            print e.msg
            sys.exit(1)


def usage():
    print(__doc__ % {'program_name': os.path.basename(sys.argv[0])})

if __name__ == '__main__':
    main()
