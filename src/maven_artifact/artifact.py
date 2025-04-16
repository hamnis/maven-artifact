import os


class Artifact:
    def __init__(self, group_id, artifact_id, version, classifier=None, extension=None):
        if not group_id:
            raise ValueError("group_id must be set")
        if not artifact_id:
            raise ValueError("artifact_id must be set")

        self.group_id = group_id
        self.artifact_id = artifact_id
        self.version = version
        self.classifier = classifier
        self.extension = extension or "jar"

    def is_snapshot(self):
        return self.version and self.version.endswith("-SNAPSHOT")

    def path(self, with_version=True):
        base = self.group_id.replace(".", "/") + "/" + self.artifact_id
        return base if not with_version else f"{base}/{self.version}"

    def uri(self, base):
        if self.is_snapshot():
            raise ValueError("Expected unique version for snapshot artifact " + str(self))
        elif not self.is_snapshot():
            resolved_version = self.version
            ret = f"{base}/{self.path()}/{self.artifact_id}-{resolved_version}"
            if self.classifier:
                ret += "-" + self.classifier
            return f"{ret}.{self.extension}"

    def with_version(self, _version):
        return Artifact(self.group_id, self.artifact_id, _version, self.classifier, self.extension)

    def _generate_filename(self):
        if not self.classifier:
            return f"{self.artifact_id}.{self.extension}"
        return f"{self.artifact_id}-{self.classifier}.{self.extension}"

    def get_filename(self, filename=None):
        if not filename:
            filename = self._generate_filename()
        elif os.path.isdir(filename):
            filename = os.path.join(filename, self._generate_filename())
        return filename

    def __str__(self):
        if self.classifier:
            return "%s:%s:%s:%s:%s" % (self.group_id, self.artifact_id, self.extension, self.classifier, self.version)
        elif self.extension != "jar":
            return "%s:%s:%s:%s" % (self.group_id, self.artifact_id, self.extension, self.version)
        else:
            return "%s:%s:%s" % (self.group_id, self.artifact_id, self.version)

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
    def parse(maven_coordinate):
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
