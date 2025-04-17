from maven_artifact import Resolver
from maven_artifact.artifact import Artifact


def test_resolve_artifact():
    resolver = Resolver.default()
    parsed_artifact = Artifact.parse("javax.servlet:servlet-api:latest")
    assert parsed_artifact.resolved_version is None
    resolved = resolver.resolve(parsed_artifact)
    assert resolved.resolved_version == "3.0-alpha-1"
    assert resolved.version == "latest"
    uri = resolver.uri_for_artifact(parsed_artifact)
    other_uri = resolved.uri(resolver.base)
    assert uri == "https://repo1.maven.org/maven2/javax/servlet/servlet-api/3.0-alpha-1/servlet-api-3.0-alpha-1.jar"
    assert other_uri == uri
