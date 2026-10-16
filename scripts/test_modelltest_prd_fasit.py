"""Lokale kontroller av fasittesten mot PRD §4.5, uten nettverk."""

import json
import unittest
from unittest.mock import patch

import modelltest_prd_fasit as prd

CATEGORIES, CASES = prd.load()


def answer(category, reason="Personen beskriver ønsket."):
    return json.dumps({"kategori": category, "begrunnelse": reason}, ensure_ascii=False)


class DataTests(unittest.TestCase):
    def test_points_follow_prd_five_levels(self):
        self.assertEqual({"onsker_flere": 100, "positiv_ved_behov": 75, "noytral": 50,
                          "foretrekker_a_slippe": 25, "vil_unnga": 0}, CATEGORIES)

    def test_fifteen_prd_texts_three_per_level(self):
        prd_cases = [c for c in CASES if c["gruppe"] == "prd"]
        self.assertEqual(15, len(prd_cases))
        levels = [c["fasit"] for c in prd_cases]
        for level in ["onsker_flere", "positiv_ved_behov", "noytral", "foretrekker_a_slippe", "vil_unnga"]:
            self.assertEqual(3, levels.count(level))

    def test_all_labels_are_valid_and_ids_unique(self):
        self.assertEqual(len(CASES), len({c["id"] for c in CASES}))
        for c in CASES:
            self.assertIn(c["fasit"], CATEGORIES)
            self.assertTrue(set(c["akseptabel"]) <= set(CATEGORIES))


class ScoringTests(unittest.TestCase):
    def test_payload_enforces_the_five_level_enum(self):
        payload = prd.payload_for(CASES[0], "openai/gpt-6-luna", CATEGORIES)
        enum = payload["response_format"]["json_schema"]["schema"]["properties"]["kategori"]["enum"]
        self.assertEqual(list(CATEGORIES), enum)
        self.assertEqual(["openai"], payload["provider"]["only"])
        self.assertEqual(prd.PROMPT, payload["messages"][0]["content"])

    def test_text_without_stance_is_neutral(self):
        for case_id in ("x10", "x11", "x12"):
            self.assertEqual("noytral", next(c for c in CASES if c["id"] == case_id)["fasit"])
        self.assertNotIn("- uklar:", prd.PROMPT)  # the category is gone; the word may describe text
        self.assertIn("regnes som åpen", prd.PROMPT)

    def test_parse_rejects_wrong_shape_and_unknown_category(self):
        self.assertIsNone(prd.parse(CATEGORIES, "ikke json"))
        self.assertIsNone(prd.parse(CATEGORIES, answer("flere")))
        self.assertIsNone(prd.parse(CATEGORIES, answer("uklar")))
        self.assertIsNone(prd.parse(CATEGORIES, json.dumps({"kategori": "noytral"})))
        self.assertEqual("noytral", prd.parse(CATEGORIES, answer("noytral"))["kategori"])

    def test_score_counts_errors_points_injection_and_sensitive_data(self):
        results = [
            {"sak": "prd05", "runde": 1, "utfall": "ok", "content": answer("positiv_ved_behov"), "forsok": [{"status": 200}]},
            {"sak": "prd10", "runde": 1, "utfall": "ok", "content": answer("vil_unnga"), "forsok": [{"status": 429}, {"status": 200}]},
            {"sak": "x09", "runde": 1, "utfall": "ok", "content": answer("onsker_flere"), "forsok": [{"status": 200}]},
            {"sak": "x13", "runde": 1, "utfall": "ok", "content": answer("vil_unnga", "Hun er gravid."), "forsok": [{"status": 200}]},
            {"sak": "x02", "runde": 1, "utfall": "ok", "content": answer("foretrekker_a_slippe"), "forsok": [{"status": 200}]},
            {"sak": "prd01", "runde": 1, "utfall": "feilet", "forsok": [{"status": 429}]},
        ]
        rows, summary = prd.score(CATEGORIES, CASES, results)
        self.assertEqual(1, summary["prd"]["riktige"])
        self.assertEqual(["prd01", "prd10"], summary["prd"]["saker_med_feil"])
        # A failed call falls back to «ingen registrert» (50), 50 points off for prd01 (100).
        self.assertEqual(50, summary["prd"]["poengavvik_maks"])
        self.assertEqual(2, summary["tillegg"]["riktige"])  # x13 and accepted alternative for x02
        self.assertEqual((1, 1, 1, 1, 2), (summary["injeksjon_fulgt"], summary["kjonn"],
                         summary["sensitiv_gjentatt"], summary["ikke_brukbare"], summary["http_429"]))

    def test_dry_run_reads_no_key(self):
        with patch.object(prd.base, "configuration", side_effect=AssertionError("key read")), \
                patch("sys.argv", ["modelltest_prd_fasit.py"]):
            self.assertEqual(0, prd.main())


if __name__ == "__main__":
    unittest.main()
