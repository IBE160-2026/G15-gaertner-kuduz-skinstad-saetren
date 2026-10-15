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
                result = probe.check_answer(case, content)
                self.assertTrue(result["format"])
                self.assertEqual([], result["innhold"])

    def test_unknown_category_is_format_error_not_category_error(self):
        result = probe.check_answer(probe.cases()[1], json.dumps({
            "kategori": "færre", "begrunnelse": "Vil ha færre vakter."}))
        self.assertTrue(result["format"])
        self.assertEqual([], result["innhold"])

    def test_rejects_wrong_semantics_despite_valid_shape(self):
        result = probe.check_answer(probe.cases()[0], json.dumps({
            "kategori": "faerre", "begrunnelse": "En begrunnelse"}))
        self.assertEqual([], result["format"])
        self.assertTrue(result["innhold"])

    def test_accepts_expected_preference(self):
        self.assertEqual({"format": [], "innhold": []}, probe.check_answer(probe.cases()[0], json.dumps({
            "kategori": "flere", "begrunnelse": "Vil ha flere vakter."})))

    def test_rejects_wrong_candidate(self):
        case = next(c for c in probe.cases() if c["kind"] == "forklaring")
        self.assertTrue(probe.check_answer(case, json.dumps({
            "kandidat_id": "UKJENT", "avveining": "En forklaring."}))["innhold"])

    def test_request_contains_no_fasit_and_no_calculation_output(self):
        for model in probe.MODELS:
            for case in probe.cases():
                with self.subTest(model=model, case=case["id"]):
                    payload = probe.payload_for(case, model)
                    self.assertEqual(case["input"], json.loads(payload["messages"][1]["content"]))
                    self.assertNotIn("expected", json.dumps(payload))
                    self.assertFalse(payload["reasoning"]["enabled"])
                    self.assertFalse(payload["provider"]["allow_fallbacks"])
                    self.assertTrue(payload["provider"]["require_parameters"])

    def test_schema_mode_and_provider_lock_per_model(self):
        case = probe.cases()[0]
        haiku = probe.payload_for(case, probe.MODEL)
        self.assertTrue(haiku["response_format"]["json_schema"]["strict"])
        self.assertNotIn("only", haiku["provider"])
        gemma = probe.payload_for(case, "google/gemma-4-31b-it:free")
        self.assertEqual({"type": "json_object"}, gemma["response_format"])
        self.assertEqual(["google-ai-studio"], gemma["provider"]["only"])
        for model, provider in [("openai/gpt-6-luna", "openai"), ("mistralai/mistral-small-2603", "mistral")]:
            payload = probe.payload_for(case, model)
            self.assertTrue(payload["response_format"]["json_schema"]["strict"])
            self.assertEqual([provider], payload["provider"]["only"])

    def test_unapproved_model_is_rejected(self):
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-or-fake"}):
            with self.assertRaises(ValueError):
                probe.configuration("openai/gpt-6-luna-pro")
            self.assertEqual("openai/gpt-6-luna", probe.configuration("openai/gpt-6-luna")[1])

    def test_summary_separates_format_and_category_errors(self):
        def done(kind, fmt, content):
            return {"kind": kind, "status": "completed",
                    "failures": {"format": fmt, "innhold": content, "teknisk": []}}
        summary = probe.summarize([
            done("preferanse", [], []), done("preferanse", [], ["feil kategori"]),
            done("preferanse", ["ikke JSON"], []), done("forklaring", [], []),
            {"kind": "forklaring", "status": "failed"}])
        self.assertEqual(1, summary["formatfeil"])
        self.assertEqual(2, summary["preferanser_med_gyldig_format"])
        self.assertEqual(1, summary["kategori_riktig_av_gyldige"])
        self.assertEqual(1, summary["forklaringer_med_riktig_id"])
        self.assertEqual(1, summary["avbrutte_kall"])

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

    def test_429_is_retried_only_when_allowed_and_counted(self):
        model = "openai/gpt-6-luna"
        ok = {"model": model, "choices": [{"finish_reason": "stop", "message": {
            "content": json.dumps({"kategori": "flere", "begrunnelse": "Vil ha flere."})}}],
              "usage": {"prompt_tokens": 1, "completion_tokens": 1, "cost": 0.0}}
        listing = {"data": [{"id": model, "supported_parameters": ["structured_outputs"]}]}
        for retries, expected_exit in [(0, 2), (1, 0)]:
            with self.subTest(retries=retries), tempfile.TemporaryDirectory() as folder,                     patch.object(probe, "ROOT", Path(folder)),                     patch.object(probe, "configuration", return_value=("sk-or-fake", model)),                     patch.object(probe.subprocess, "check_output", return_value="test-baseline"),                     patch.object(probe.time, "sleep"),                     patch("sys.argv", ["probe", "--live", "--smoke", "--retry-429", str(retries)]),                     patch.object(probe, "call_api", side_effect=[
                        listing, {"data": {}}, probe.RateLimited("HTTP 429"), ok]):
                self.assertEqual(expected_exit, probe.main())
                report = json.loads(next(Path(folder).rglob("gpt6-luna-smoke-*.json")).read_text(encoding="utf-8"))
                self.assertEqual(retries, report["summary"]["http_429_for_svar"])

    def test_other_http_errors_are_not_rate_limited(self):
        error = HTTPError(probe.BASE, 500, "server", {}, None)
        with patch.object(probe, "build_opener") as opener:
            opener.return_value.open.side_effect = error
            with self.assertRaises(RuntimeError) as raised:
                probe.call_api("chat/completions", "sk-or-fake")
            self.assertNotIsInstance(raised.exception, probe.RateLimited)

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
