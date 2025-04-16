from maven_artifact import Requestor, Resolver
from maven_artifact.artifact import Artifact


def test_resolve_artifact():
    req = Requestor()
    resolver = Resolver("https://repo1.maven.org/maven2", req)
    parsed_artifact = Artifact.parse("javax.servlet:servlet-api:latest")
    resolved = resolver.resolve(parsed_artifact)
    assert resolved.version == "3.0-alpha-1"
    uri = resolver.uri_for_artifact(parsed_artifact)
    assert uri == "https://repo1.maven.org/maven2/javax/servlet/servlet-api/3.0-alpha-1/servlet-api-3.0-alpha-1.jar"
