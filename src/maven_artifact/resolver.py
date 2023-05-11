from lxml import etree

from .requestor import RequestException

class Resolver(object):
    def __init__(self, base, requestor):
        self.requestor = requestor
        if base.endswith("/"):
            base = base.rstrip("/")
        self.base = base

    def _find_latest_version_available(self, artifact):
        path = "/%s/maven-metadata.xml" % (artifact.path(False))
        xml = self.requestor.request(self.base + path, self._onFail, lambda r: etree.fromstring(r.content))
        v = xml.xpath("/metadata/versioning/versions/version[last()]/text()")
        if v:
            return v[0]

    def _find_latest_snapshot_version(self, artifact):
        path = "/%s/maven-metadata.xml" % (artifact.path())
        xml = self.requestor.request(
            self.base + path, self._onFail, lambda r: etree.fromstring(r.content)
            )
        timestamp = xml.xpath("/metadata/versioning/snapshot/timestamp/text()")[0]
        buildNumber = xml.xpath("/metadata/versioning/snapshot/buildNumber/text()")[0]
        meta_version = f"{timestamp}-{buildNumber}"
        # obtain exact version value
        versions = xml.xpath("/metadata/versioning/snapshotVersions/snapshotVersion/value/text()")
        for version in set(versions):
            if meta_version in version:
                return version
        return meta_version

    def _onFail(self, url, e):
        raise RequestException(f"Failed to download maven-metadata.xml from {url} due to {e}")

    def resolve(self, artifact):
        version = artifact.version
        if not artifact.version or artifact.version == "latest":
            version = self._find_latest_version_available(artifact)
        elif artifact.is_snapshot():
            version = self._find_latest_snapshot_version(artifact)
        return artifact.with_version(version)

    def uri_for_artifact(self, artifact):
        resolved = self.resolve(artifact)
        return artifact.uri(self.base, resolved.version)
