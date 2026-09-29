import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from clash_select import DEFAULT_CONTROLLER, resolve_config


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'config.yaml'

    def test_explicit_options_do_not_read_missing_file(self):
        with patch.object(Path, 'read_text', side_effect=AssertionError('must not read')):
            config = resolve_config('http://other.invalid:9000', 'explicit-token', self.path)
        self.assertEqual(config.base_url, 'http://other.invalid:9000')
        self.assertEqual(config.secret, 'explicit-token')

    def test_custom_destination_does_not_receive_local_secret(self):
        self.path.write_text('secret: local-fixture-token\n')
        config = resolve_config('http://other.invalid:9000', None, self.path)
        self.assertEqual(config.secret, '')

    def test_explicit_empty_secret_is_preserved(self):
        self.path.write_text('secret: local-fixture-token\n')
        self.assertEqual(resolve_config(None, '', self.path).secret, '')

    def test_explicit_secret_uses_default_controller_without_file(self):
        config = resolve_config(None, 'explicit-token', self.path)
        self.assertEqual(config.base_url, DEFAULT_CONTROLLER)
        self.assertEqual(config.secret, 'explicit-token')

    def test_file_controller_and_credentials_stay_paired(self):
        self.path.write_text('external-controller: 127.0.0.1:9191\nsecret: local-fixture-token\n')
        config = resolve_config(None, None, self.path)
        self.assertEqual(config.base_url, 'http://127.0.0.1:9191')
        self.assertEqual(config.secret, 'local-fixture-token')

    def test_wildcard_bind_address_connects_over_loopback(self):
        for address in ['0.0.0.0:9090', '[::]:9090']:
            self.path.write_text(f'external-controller: "{address}"\nsecret: ""\n')
            self.assertEqual(resolve_config(None, None, self.path).base_url, DEFAULT_CONTROLLER)

    def test_invalid_config_reports_no_file_contents(self):
        for content in ['', '[one, two]', 'secret: [private-fixture-value', 'secret: [private-fixture-value]']:
            self.path.write_text(content)
            with self.assertRaises(ValueError) as error:
                resolve_config(None, None, self.path)
            self.assertNotIn('private-fixture-value', str(error.exception))


if __name__ == '__main__':
    unittest.main()
