from lxml import etree

from maven_artifact.requestor import RequestException

from maven_artifact.requestor import Requestor


class Resolver:
    def __init__(self, base: str, requestor: Requestor):
        self.requestor = requestor
        if base.endswith("/"):
            base = base.rstrip("/")
        self.base = base

    @staticmethod
    def default():
        return Resolver("https://repo1.maven.org/maven2", Requestor())

    def _find_latest_version_available(self, artifact):
        path = f"/{artifact.path(False)}/maven-metadata.xml"
        xml = self.requestor.request(self.base + path, self._onFail, lambda r: etree.fromstring(r.content))
        v = xml.xpath("/metadata/versioning/versions/version[last()]/text()")
        return v[0] if v else None

    def _find_latest_snapshot_version(self, artifact):
        path = f"/{artifact.path()}/maven-metadata.xml"
        xml = self.requestor.request(self.base + path, self._onFail, lambda r: etree.fromstring(r.content))
        timestamp = xml.xpath("/metadata/versioning/snapshot/timestamp/text()")[0]
        build_number = xml.xpath("/metadata/versioning/snapshot/buildNumber/text()")[0]
        meta_version = f"{timestamp}-{build_number}"
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

        resolved_artifact = artifact.with_version(version)
        if resolved_artifact.is_snapshot():
            # We need to re-resolve the snapshot version to get the actual version
            resolved_version = self._find_latest_snapshot_version(resolved_artifact)
            return resolved_artifact.with_resolved_version(resolved_version)
        return artifact.with_resolved_version(version)

    def uri_for_artifact(self, artifact):
        resolved = self.resolve(artifact)
        return resolved.uri(self.base)
