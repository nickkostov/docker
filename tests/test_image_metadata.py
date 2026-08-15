import json
from pathlib import Path
import re
import unittest

from jsonschema import Draft202012Validator, FormatChecker
import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPOSITORY_ROOT / "schemas" / "image.schema.json"
IMAGE_PATHS = sorted((REPOSITORY_ROOT / "images").glob("**/image.yaml"))
FLOW_STYLE = re.compile(r"^[a-z_]+:\s*[\[{]", re.MULTILINE)


class ImageMetadataTests(unittest.TestCase):
    def test_all_definitions_are_block_style_yaml(self) -> None:
        for path in IMAGE_PATHS:
            with self.subTest(path=path.relative_to(REPOSITORY_ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertIsNone(FLOW_STYLE.search(text))
                metadata = yaml.safe_load(text)
                self.assertIsInstance(metadata, dict)
                self.assertIn(metadata["variant"], {"base", "runtime", "service"})

    def test_schema_has_no_errors_except_explicit_digest_placeholders(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())

        for path in IMAGE_PATHS:
            metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
            errors = list(validator.iter_errors(metadata))
            unexpected = [error for error in errors if not self._is_digest_placeholder(error)]
            with self.subTest(path=path.relative_to(REPOSITORY_ROOT)):
                self.assertEqual([], unexpected, "\n".join(error.message for error in unexpected))

    @staticmethod
    def _is_digest_placeholder(error: object) -> bool:
        instance = getattr(error, "instance", None)
        path = list(getattr(error, "absolute_path", []))
        return (
            getattr(error, "validator", None) == "pattern"
            and path
            and path[-1] == "digest"
            and isinstance(instance, str)
            and instance.startswith("sha256:REPLACE_WITH_")
        )


if __name__ == "__main__":
    unittest.main()
