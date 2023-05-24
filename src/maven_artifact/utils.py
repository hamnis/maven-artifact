import base64

from maven_artifact.artifact import Artifact


class Utils:

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
    
    @staticmethod
    def is_base64(sb):
        try:
            if isinstance(sb, str):
                # If there's any unicode here, an exception will be thrown and the function will return false
                sb_bytes = bytes(sb, "ascii")
            elif isinstance(sb, bytes):
                sb_bytes = sb
            else:
                raise ValueError("Argument must be string or bytes")
            return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
        except Exception:
            return False

