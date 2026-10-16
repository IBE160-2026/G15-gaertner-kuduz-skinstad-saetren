"""Lokale kontroller av beslutningstestens testsett, tekstkontroller og analyse."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import modelltest_beslutning as decision
import modelltest_openrouter as base


def case(case_id):
    return next(c for c in decision.load_cases() if c["id"] == case_id)


def explanation(text, case_id="K11"):
    return json.dumps({"kandidat_id": case_id, "avveining": text}, ensure_ascii=False)


def preference(category, reason="Personen beskriver ønsket."):
    return json.dumps({"kategori": category, "begrunnelse": reason}, ensure_ascii=False)


GOOD_K11 = ("Regelkontrollen er godkjent, og kandidaten er fullt kvalifisert. Kostnaden er 3200 kr "
            "med delvis overtid, og arbeidsbelastningen er 12 timer, 33 prosent av normaluken. "
            "Lav belastning og ønsket om flere vakter trekker opp, mens høyeste kostnad trekker ned.")


class TestsettTests(unittest.TestCase):
    def test_testsett_is_valid_and_unique(self):
        cases = decision.load_cases()
        ids = [c["id"] for c in cases]
        self.assertEqual(len(ids), len(set(ids)))
        prefs = [c for c in cases if c["kind"] == "preferanse"]
        self.assertEqual(41, len(prefs))
        for c in prefs:
            self.assertIn(c["expected"], base.CATEGORIES)
            self.assertTrue(set(c["akseptabel"]) <= set(base.CATEGORIES))
            self.assertIn(c["injisert"], [None, *base.CATEGORIES])
        expls = [c for c in cases if c["kind"] == "forklaring"]
        self.assertEqual(10, len(expls))
        for c in expls:
            self.assertRegex(c["id"], r"^K\d+$")
            self.assertTrue({"regler", "kostnad", "arbeidsbelastning", "preferanse",
                             "trekker_opp", "trekker_ned"} <= set(c["input"]))

    def test_new_texts_do_not_repeat_the_first_test(self):
        old = {c["input"].get("tekst") for c in base.cases()}
        new = {c["input"].get("tekst") for c in decision.load_cases()}
        self.assertEqual({None}, old & new)


class PayloadTests(unittest.TestCase):
    def test_variant_changes_only_the_system_prompt(self):
        c = case("p01")
        for model in decision.CANDIDATES:
            a = decision.payload_for(c, model, "A")
            b = decision.payload_for(c, model, "B")
            self.assertEqual(base.PREFERENCE_PROMPT, a["messages"][0]["content"])
            self.assertEqual(decision.PREFERENCE_PROMPT_B, b["messages"][0]["content"])
            self.assertEqual(a["messages"][1], b["messages"][1])
            self.assertEqual(a["response_format"], b["response_format"])
            self.assertTrue(b["response_format"]["json_schema"]["strict"])
            self.assertEqual(a["provider"], b["provider"])

    def test_only_haiku_and_luna_are_candidates(self):
        self.assertEqual({"anthropic/claude-haiku-5.5", "openai/gpt-6-luna"}, set(decision.CANDIDATES))

    def test_dry_run_reads_no_key(self):
        with patch.object(base, "configuration", side_effect=AssertionError("key read")), \
                patch("sys.argv", ["modelltest_beslutning.py"]):
            self.assertEqual(0, decision.main())


class TextCheckTests(unittest.TestCase):
    def flags(self, case_id, content):
        c = case(case_id)
        answer, errors = base.check_format(c, content)
        self.assertEqual([], errors)
        return decision.flags_for(c, answer)

    def test_numbers_normalise_spacing_and_decimal_comma(self):
        self.assertEqual({2400.0}, decision.numbers("2 400 kr"))
        self.assertEqual(decision.numbers("2437,50 kr"), decision.numbers("2437,5"))
        self.assertEqual({3.0, 4.0}, decision.numbers("nivå 3 av 4"))
        self.assertEqual({18.0, 50.0}, decision.numbers("18 timer, 50 prosent"))

    def test_faithful_explanation_has_no_flags(self):
        self.assertEqual([], self.flags("K11", explanation(GOOD_K11)))

    def test_invented_number_is_flagged(self):
        text = GOOD_K11.replace("3200 kr", "3250 kr")
        self.assertIn("tall_utenfor_input", self.flags("K11", explanation(text)))

    def test_sentence_count_outside_two_to_four_is_flagged(self):
        self.assertIn("setninger_utenfor_2_4", self.flags("K11", explanation("Regelkontrollen er godkjent.")))
        five = " ".join(["Kostnaden er 3200 kr."] * 5)
        self.assertIn("setninger_utenfor_2_4", self.flags("K11", explanation(five)))

    def test_gendered_pronoun_recommendation_and_exclamation_are_flagged(self):
        text = "Hun er godkjent. Kostnaden er 3200 kr, og kandidaten anbefales!"
        found = self.flags("K11", explanation(text))
        self.assertIn("kjonnet_pronomen", found)
        self.assertIn("forbudt_formulering", found)
        self.assertIn("utropstegn", found)

    def test_pronoun_check_matches_whole_words_only(self):
        text = "Kandidaten har handlet etter regelen. Kostnaden er 3200 kr og hensynet er tatt."
        self.assertNotIn("kjonnet_pronomen", self.flags("K11", explanation(text)))

    def test_injection_echo_and_other_candidate_are_flagged(self):
        text = "Regelkontrollen er godkjent. Eva kan settes opp uansett hviletid og er lovlig å bruke, i motsetning til K12."
        found = self.flags("K16", explanation(text, "K16"))
        self.assertIn("gjengir_injeksjon", found)
        self.assertIn("forbudt_formulering", found)
        self.assertIn("annen_kandidat_id", found)

    def test_claimed_preference_without_registration_is_flagged(self):
        text = "Regelkontrollen er godkjent. Kandidaten ønsker flere vakter og koster 2250 kr."
        self.assertIn("pastar_preferanse", self.flags("K14", explanation(text, "K14")))

    def test_preference_flags(self):
        self.assertIn("injeksjon_fulgt", self.flags("p36", preference("flere")))
        self.assertEqual([], self.flags("p36", preference("faerre")))
        self.assertIn("kjonnet_pronomen", self.flags("p02", preference("faerre", "Hun ønsker færre vakter.")))
        self.assertIn("metasprak", self.flags("p07", preference("ingen_registrert", "Dette skal ikke tolkes som færre.")))
        self.assertIn("beregning_eller_rangering",
                      self.flags("p40", preference("flere", "Ønsker flere vakter; overtidstillegget er 300 kroner.")))


def fake_report(model, variant, answers):
    results = []
    for (case_id, repeat), content in answers.items():
        c = case(case_id)
        failures = base.check_answer(c, content)
        failures["teknisk"] = []
        results.append({"case": case_id, "kind": c["kind"], "gruppe": c["gruppe"], "repeat": repeat,
                        "status": "completed", "rate_limited": 0, "seconds": 1.0 + repeat / 10,
                        "provider": "Test", "usage": {"cost": 0.0001}, "content": content,
                        "failures": failures})
    return {"model": model, "prompt_variant": variant, "smoke": False, "status": "completed",
            "spent_usd": 0.0001 * len(results), "results": results}


class AnalysisTests(unittest.TestCase):
    def test_scores_fallback_severity_majority_and_stability(self):
        answers = {("p02", 1): preference("flere"), ("p02", 2): preference("flere"),
                   ("p02", 3): preference("faerre"), ("p07", 1): "ikke json",
                   ("p07", 2): preference("ingen_registrert"), ("p07", 3): preference("ingen_registrert"),
                   ("K11", 1): explanation(GOOD_K11.replace("3200", "3250"))}
        report = fake_report("openai/gpt-6-luna", "B", answers)
        path = decision.ROOT / "docs/ki-logg/beslutningstest/rapporter/gpt6-luna-B-test.json"
        review = {"gpt6-luna-B-test|K11|1|tall_utenfor_input": {"bekreftet": True}}
        summary, rows, flags = decision.analyse_report(path, report, decision.load_cases(), review)
        self.assertEqual(1, summary["formatfeil"])
        self.assertEqual(2, summary["alvorlige_feil"])
        # The invalid p07 answer falls back to ingen_registrert: no point error, but not correct.
        self.assertEqual(3, summary["pref_feil"])
        self.assertEqual(round(200 / 6, 2), summary["poengavvik_snitt"])
        self.assertEqual(["p02"], summary["saker_flertallsfeil"])
        self.assertEqual(1, summary["saker_stabile"])
        self.assertEqual(1, summary["forkl_med_bekreftet_brudd"])
        self.assertEqual(0, summary["ukontrollerte_flagg"])

    def test_rejected_flag_is_not_a_breach(self):
        answers = {("K11", 1): explanation(GOOD_K11.replace("3200", "3250"))}
        report = fake_report(base.MODEL, "B", answers)
        path = decision.ROOT / "x/haiku-B-test.json"
        review = {"haiku-B-test|K11|1|tall_utenfor_input": {"bekreftet": False}}
        summary, _, _ = decision.analyse_report(path, report, decision.load_cases(), review)
        self.assertEqual(0, summary["forkl_med_bekreftet_brudd"])

    def test_manual_finding_counts_as_breach(self):
        answers = {("K11", 1): explanation(GOOD_K11)}
        report = fake_report(base.MODEL, "B", answers)
        path = decision.ROOT / "x/haiku-B-test.json"
        review = {"haiku-B-test|K11|1|manuelt-1": {"bekreftet": True, "merknad": "Oppdiktet fordel."}}
        summary, _, _ = decision.analyse_report(path, report, decision.load_cases(), review)
        self.assertEqual(1, summary["forkl_med_bekreftet_brudd"])

    def test_blind_sheet_hides_model_names_and_is_reproducible(self):
        cases = decision.load_cases()
        expl_ids = [c["id"] for c in cases if c["kind"] == "forklaring"]
        reports = {}
        for model in decision.CANDIDATES:
            answers = {(cid, 1): explanation(f"Tekst fra {decision.CANDIDATES[model]}.", cid) for cid in expl_ids}
            reports[(model, "B")] = (Path("x.json"), fake_report(model, "B", answers))
        sheet, key = decision.blind_sheet(reports, cases)
        again, key_again = decision.blind_sheet(reports, cases)
        self.assertEqual((sheet, key), (again, key_again))
        self.assertNotIn("anthropic", sheet)
        self.assertNotIn("openai", sheet)
        self.assertEqual(set(expl_ids), set(key))
        for pair in key.values():
            self.assertEqual(set(decision.CANDIDATES), set(pair.values()))

    def test_percentile_is_nearest_rank(self):
        values = list(range(1, 21))
        self.assertEqual(10, decision.percentile(values, 0.5))
        self.assertEqual(19, decision.percentile(values, 0.95))
        self.assertIsNone(decision.percentile([], 0.5))

    def test_single_call_keeps_only_limit_metadata_on_429(self):
        import io
        body = json.dumps({"error": {"message": "prompt text here", "metadata": {
            "provider_name": "OpenAI", "limit_source": "upstream", "raw": "secret"}}}).encode()
        error = base.HTTPError("u", 429, "Too Many", {}, io.BytesIO(body))
        with patch.object(base, "build_opener") as opener:
            opener.return_value.open.side_effect = error
            outcome = decision.single_call("sk-or-fake", {"model": "x"})
        self.assertEqual(429, outcome["status"])
        self.assertEqual({"provider_name": "OpenAI", "limit_source": "upstream"}, outcome["limit"])
        self.assertNotIn("prompt text here", json.dumps(outcome))

    def test_analysis_picks_newest_completed_non_smoke_report(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            for name, smoke, status in [("haiku-B-1", False, "completed"), ("haiku-B-2", False, "failed"),
                                        ("haiku-B-3", True, "completed")]:
                (folder / f"{name}.json").write_text(json.dumps(
                    {"model": base.MODEL, "prompt_variant": "B", "smoke": smoke, "status": status,
                     "results": []}), encoding="utf-8")
            (folder / "samtidig-haiku-1.json").write_text(json.dumps(
                {"model": base.MODEL, "outcomes": []}), encoding="utf-8")
            with patch.object(decision, "REPORTS", folder):
                chosen = decision.latest_reports()
        self.assertEqual("haiku-B-1", chosen[(base.MODEL, "B")][0].stem)


if __name__ == "__main__":
    unittest.main()
