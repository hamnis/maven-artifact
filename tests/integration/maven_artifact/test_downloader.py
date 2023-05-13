import os
import tempfile

from maven_artifact import Artifact, Downloader


def test_downloader_of_existing_artifact():
    artifact = Artifact.parse("org.apache.solr:solr:war:3.5.0")

    dl = Downloader()

    tmpdirname = tempfile.TemporaryDirectory()

    tmpfile = os.path.join(tmpdirname.name, "example.war")

    dl.download(artifact, filename=tmpfile)

    assert os.path.exists(tmpfile)

    tmpdirname.cleanup()
