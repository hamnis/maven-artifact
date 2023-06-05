import pytest
from maven_artifact import Artifact


def test_artifact_missing_params():
    with pytest.raises(TypeError):
        Artifact()


def test_issnapshot():
    artifact = Artifact(
        group_id="com.example", artifact_id="example-artifact", version="0.0.1", classifier="javadoc", extension="zip"
    )

    assert artifact.is_snapshot() is False

    artifact = artifact.with_version(_version="0.0.1-SNAPSHOT")

    assert artifact.is_snapshot() is True


@pytest.mark.parametrize("test_input,expected", [("group:artifact:version", Artifact(group_id="group", artifact_id="artifact", version="version")), ("group:artifact:extension:version", Artifact(group_id="group", artifact_id="artifact", version="version", extension="extension")), ("group:artifact:extension:classifier:version", Artifact(group_id="group", artifact_id="artifact", version="version", extension="extension", classifier="classifier"))])
def test_eq(test_input, expected):
    assert Artifact.parse(test_input) == expected
