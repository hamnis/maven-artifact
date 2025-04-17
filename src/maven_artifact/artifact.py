import copy
import os
from typing import Optional


class Artifact:
    def __init__(
        self,
        group_id: str,
        artifact_id: str,
        version: Optional[str],
        classifier: Optional[str] = None,
        extension: Optional[str] = None,
    ):
        if not group_id:
            raise ValueError("group_id must be set")
        if not artifact_id:
            raise ValueError("artifact_id must be set")

        self.group_id = group_id
        self.artifact_id = artifact_id
        self.version = version
        self.classifier = classifier
        self.extension = extension or "jar"
        self.resolved_version = None

    def is_snapshot(self):
        return self.version and self.version.endswith("-SNAPSHOT")

    def path(self, with_version: bool = True):
        base = self.group_id.replace(".", "/") + "/" + self.artifact_id
        actual_version = self.version if self.version != "latest" else self.resolved_version
        return base if not with_version else f"{base}/{actual_version}"

    def uri(self, base: str):
        if self.is_snapshot() and not self.resolved_version:
            raise ValueError("Expected unique version for snapshot artifact " + str(self))
        if self.resolved_version:
            actual_version = self.resolved_version
        else:
            actual_version = self.version

        ret = f"{base}/{self.path()}/{self.artifact_id}-{actual_version}"
        if self.classifier:
            ret += "-" + self.classifier
        return f"{ret}.{self.extension}"

    def with_version(self, version: str):
        artifact = copy.copy(self)
        artifact.version = version
        return artifact

    def with_classifier(self, classifier: str):
        artifact = copy.copy(self)
        artifact.classifier = classifier
        return artifact

    def with_resolved_version(self, version: str):
        artifact = copy.copy(self)
        artifact.resolved_version = version
        return artifact

    def _generate_filename(self):
        if not self.classifier:
            return f"{self.artifact_id}.{self.extension}"
        return f"{self.artifact_id}-{self.classifier}.{self.extension}"

    def get_filename(self, filename: Optional[str] = None):
        if not filename:
            filename = self._generate_filename()
        elif os.path.isdir(filename):
            filename = os.path.join(filename, self._generate_filename())
        return filename

    def __str__(self):
        if self.classifier:
            return f"{self.group_id}:{self.artifact_id}:{self.extension}:{self.classifier}:{self.version}"
        elif self.extension != "jar":
            return f"{self.group_id}:{self.artifact_id}:{self.extension}:{self.version}"
        else:
            return f"{self.group_id}:{self.artifact_id}:{self.version}"

    def __eq__(self, other):
        return (
            isinstance(other, Artifact)
            and self.group_id == other.group_id
            and self.artifact_id == other.artifact_id
            and self.version == other.version
            and self.classifier == other.classifier
            and self.extension == other.extension
        )

    @staticmethod
    def parse(maven_coordinate: str):
        parts = maven_coordinate.split(":")
        if len(parts) >= 3:
            g = parts[0]
            a = parts[1]
            v = parts[len(parts) - 1]
            t = None
            c = None
            if len(parts) == 4:
                t = parts[2]
            if len(parts) == 5:
                t = parts[2]
                c = parts[3]
            return Artifact(group_id=g, artifact_id=a, version=v, classifier=c, extension=t)
        else:
            return None
