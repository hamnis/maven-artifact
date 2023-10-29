#!/bin/env python

import argparse
import os
import sys
import textwrap
from importlib.metadata import version
from maven_artifact.artifact import Artifact

try:
    from maven_artifact.utils import Utils
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from maven_artifact.utils import Utils

from maven_artifact.requestor import RequestException
from maven_artifact.downloader import Downloader


class DescriptionWrappedNewlineFormatter(argparse.HelpFormatter):
    """An argparse formatter that:
    * preserves newlines (like argparse.RawDescriptionHelpFormatter),
    * removes leading indent (great for multiline strings),
    * and applies reasonable text wrapping.

    Source: https://stackoverflow.com/a/64102901/79125
    """

    def _fill_text(self, text, width, indent):
        # Strip the indent from the original python definition that plagues most of us.
        text = textwrap.dedent(text)
        text = textwrap.indent(text, indent)  # Apply any requested indent.
        text = text.splitlines()  # Make a list of lines
        text = [textwrap.fill(line, width) for line in text]  # Wrap each line
        text = "\n".join(text)  # Join the lines again
        return text


class WrappedNewlineFormatter(DescriptionWrappedNewlineFormatter):
    """An argparse formatter that:
    * preserves newlines (like argparse.RawTextHelpFormatter),
    * removes leading indent and applies reasonable text wrapping (like DescriptionWrappedNewlineFormatter),
    * applies to all help text (description, arguments, epilogue).
    """

    def _split_lines(self, text, width):
        # Allow multiline strings to have common leading indentation.
        text = textwrap.dedent(text)
        text = text.splitlines()
        lines = []
        for line in text:
            wrapped_lines = textwrap.fill(line, width).splitlines()
            lines.extend(subline for subline in wrapped_lines)
            if line:
                lines.append("")  # Preserve line breaks.
        return lines


class MainCommand:
    def _get_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=WrappedNewlineFormatter, epilog=__epilog__)
        parser.add_argument(
            "-V",
            "--version",
            action="version",
            version=version("maven-artifact"),
        )

        parser.add_argument(
            "maven_coordinate",
            help="""
            defined by http://maven.apache.org/pom.html#Maven_Coordinates. The possible options are:
            - groupId:artifactId:version
            - groupId:artifactId:packaging:version
            - groupId:artifactId:packaging:classifier:version""",
        )
        parser.add_argument(
            "filename",
            nargs="?",
            help="""
            If not supplied the filename will be <artifactId>.<extension>.
            The filename directory must exist prior to download.""",
        )
        parser.add_argument(
            "-m",
            "--maven-repo",
            dest="base",
            default="https://repo.maven.apache.org/maven2/",
            help="Maven repository URL (default: https://repo.maven.apache.org/maven2/)",
        )

        parser.add_argument("-u", "--username", help="username (must be combined with --password)")
        parser.add_argument(
            "-p",
            "--password",
            help="""
            password (must be combined with --username) or
            base64 encoded username and password (can not not be combined with --username)""",
        )
        parser.add_argument(
            "-t", "--token", help="OAuth bearer token (can not be combined with --username or --password)"
        )

        parser.add_argument("-ht", "--hash-type", default="md5", help="hash type (default: md5)")

        args = parser.parse_args()

        username = args.username
        password = args.password
        token = args.token

        if username and not password:
            parser.error("The 'username' parameter requires the 'password' parameter.")
        elif (username or password) and token:
            parser.error("The 'token' parameter cannot be used together with 'username' or 'password'.")
        elif (password) and not (username or token) and not Utils.is_base64(password):
            parser.error("The 'password' parameter must be base64 if not used together with 'username'.")

        return args


__epilog__ = """
            Example:
                %(prog)s "org.apache.solr:solr:war:3.5.0"\n
            """


def main():
    mc = MainCommand()
    args = mc._get_arguments()

    try:
        dl = Downloader(base=args.base, username=args.username, password=args.password, token=args.token)

        artifact = Artifact.parse(args.maven_coordinate)

        filename = args.filename

        if dl.download(artifact, filename, args.hash_type):
            sys.exit(0)
        else:
            print("Download failed.")
            sys.exit(1)
    except RequestException as e:
        print(e.msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
