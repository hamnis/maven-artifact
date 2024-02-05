import base64
from importlib.metadata import version


class Utils:
    is_installed_package = True

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

    @staticmethod
    def get_version():
        return f"{version('maven-artifact')}" if Utils.is_installed_package else "non-pip-package"
