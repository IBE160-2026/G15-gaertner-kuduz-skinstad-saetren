"""Lokale kontroller av at måleverktøyet avdekker ugyldige modellsvar."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import modelltest_openrouter as probe


class ResponseChecks(unittest.TestCase):
    def test_rejects_invalid_or_incomplete_json(self):
        case = probe.cases()[0]
        for content in [None, "", "```json\n{}\n```", "[]", "null", "{}",
                        '{"kategori":"flere","begrunnelse":null}',
                        '{"kategori":"flere","begrunnelse":""}',
                        '{"kategori":"flere","begrunnelse":"OK","poeng":100}']:
            with self.subTest(content=content):
                self.assertTrue(probe.check_answer(case, content))

    def test_rejects_wrong_semantics_despite_valid_shape(self):
        self.assertTrue(probe.check_answer(probe.cases()[0], json.dumps({
            "kategori": "faerre", "begrunnelse": "En begrunnelse"})))

    def test_accepts_expected_preference(self):
        self.assertEqual([], probe.check_answer(probe.cases()[0], json.dumps({
            "kategori": "flere", "begrunnelse": "Vil ha flere vakter."})))

    def test_rejects_wrong_candidate(self):
        case = next(c for c in probe.cases() if c["kind"] == "forklaring")
        self.assertTrue(probe.check_answer(case, json.dumps({
            "kandidat_id": "UKJENT", "avveining": "En forklaring."})))

    def test_request_contains_no_fasit_and_no_calculation_output(self):
        for case in probe.cases():
            payload = probe.payload_for(case, probe.MODEL)
            self.assertEqual(case["input"], json.loads(payload["messages"][1]["content"]))
            self.assertTrue(payload["response_format"]["json_schema"]["strict"])
            self.assertFalse(payload["reasoning"]["enabled"])
            self.assertFalse(payload["provider"]["allow_fallbacks"])

    def test_dry_run_never_reads_key_or_contacts_api(self):
        with patch("sys.argv", ["probe"]), patch.object(probe, "configuration") as config, \
                patch.object(probe, "call_api") as api:
            self.assertEqual(0, probe.main())
            config.assert_not_called()
            api.assert_not_called()

    def test_report_redacts_secret_even_when_model_echoes_it(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "report.json"
            secret = "sk-or-v1-fake-secret-for-unit-test"
            probe.write_report(output, {"content": secret + " sk-or-another-fake"}, secret)
            content = output.read_text(encoding="utf-8")
            self.assertNotIn(secret, content)
            self.assertNotIn("sk-or-", content)
            self.assertIn("[REDACTED]", content)

    def test_error_does_not_expose_server_message(self):
        error = HTTPError(probe.BASE, 401, "sk-or-fake-secret", {}, None)
        with patch.object(probe, "build_opener") as opener:
            opener.return_value.open.side_effect = error
            with self.assertRaisesRegex(RuntimeError, r"^HTTP 401 fra OpenRouter") as raised:
                probe.call_api("key", "sk-or-fake-secret")
            self.assertNotIn("sk-or-", str(raised.exception))

    def test_redirects_are_blocked(self):
        self.assertIsNone(probe.NoRedirect().redirect_request(None, None, 302, "", {},
                                                             "https://example.org"))

    def test_bad_message_is_recorded_as_failed_attempt(self):
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(probe, "ROOT", Path(folder)), \
                patch.object(probe, "configuration", return_value=("sk-or-fake", probe.MODEL)), \
                patch.object(probe.subprocess, "check_output", return_value="test-baseline"), \
                patch("sys.argv", ["probe", "--live"]), \
                patch.object(probe, "call_api", side_effect=[
                    {"data": [{"id": probe.MODEL, "supported_parameters": ["structured_outputs"]}]},
                    {"data": {}}, {"choices": [{"message": None}]}]):
            self.assertEqual(2, probe.main())
            report_path = next(Path(folder).rglob("haiku-*.json"))
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual("failed", report["status"])
            self.assertEqual("failed", report["results"][0]["status"])
            self.assertEqual("flere", report["results"][0]["case"])
            self.assertIn("request", report["results"][0])


if __name__ == "__main__":
    unittest.main()
