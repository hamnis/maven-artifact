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
