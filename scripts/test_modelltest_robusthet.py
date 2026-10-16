"""Lokale kontroller av retry-politikken i robusthetstesten, uten nettverk."""

import json
import random
import threading
import time
import unittest
from unittest.mock import patch

import modelltest_beslutning as decision
import modelltest_robusthet as robust

CASE = next(c for c in decision.load_cases() if c["id"] == "K11")
GOOD = {"status": 200, "content": json.dumps({"kandidat_id": "K11", "avveining": "Godkjent. Kostnaden er 3200 kr."}),
        "finish_reason": "stop", "usage": {"cost": 0.0001}, "seconds": 0.1}


def limited(headers=None):
    return {"status": 429, "headers": headers or {}, "seconds": 0.01, "limit_source": "openrouter_new_account"}


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.waits = []

    def sleep(self, seconds):
        self.waits.append(seconds)
        self.now += seconds

    def clock(self):
        return self.now


def run(responses, policy=robust.POLICY):
    clock = FakeClock()
    sequence = iter(responses)
    outcome = robust.call_with_policy("sk-or-fake", {}, CASE, policy, threading.BoundedSemaphore(1),
                                      random.Random(1), send=lambda k, p: next(sequence),
                                      sleep=clock.sleep, clock=clock.clock)
    return outcome, clock


class PolicyTests(unittest.TestCase):
    def test_success_without_retry(self):
        outcome, clock = run([GOOD])
        self.assertEqual("ok", outcome["utfall"])
        self.assertEqual([], clock.waits)

    def test_429_is_retried_with_backoff_then_succeeds(self):
        outcome, clock = run([limited(), limited(), GOOD])
        self.assertEqual("ok", outcome["utfall"])
        self.assertEqual(3, len(outcome["forsok"]))
        self.assertTrue(1.0 <= clock.waits[0] <= 1.25 and 2.0 <= clock.waits[1] <= 2.5)

    def test_retry_after_header_is_honoured_and_capped(self):
        _, clock = run([limited({"retry-after": "3"}), limited({"retry-after": "60"}), GOOD])
        self.assertEqual([3.0, robust.POLICY["retry_after_maks_s"]], clock.waits)

    def test_gives_up_when_budget_would_be_exceeded(self):
        outcome, clock = run([limited({"retry-after": "10"})] * 10)
        self.assertEqual("feilet", outcome["utfall"])
        self.assertLessEqual(sum(clock.waits), robust.POLICY["budsjett_s"])

    def test_gives_up_after_last_backoff_step(self):
        outcome, _ = run([limited()] * 10, dict(robust.POLICY, budsjett_s=1000))
        self.assertEqual("feilet", outcome["utfall"])
        self.assertEqual(len(robust.POLICY["backoff_s"]) + 1, len(outcome["forsok"]))

    def test_402_and_400_are_not_retried(self):
        for status in (402, 400):
            outcome, clock = run([{"status": status, "headers": {}, "seconds": 0.01}, GOOD])
            self.assertEqual("feilet", outcome["utfall"])
            self.assertEqual([], clock.waits)

    def test_transient_server_and_network_errors_are_retried(self):
        for status in (503, "nettverksfeil"):
            outcome, _ = run([{"status": status, "headers": {}, "seconds": 0.01}, GOOD])
            self.assertEqual("ok", outcome["utfall"])

    def test_unusable_answer_is_not_retried(self):
        outcome, clock = run([dict(GOOD, content="ikke json"), GOOD])
        self.assertEqual("ubrukelig", outcome["utfall"])
        self.assertEqual([], clock.waits)
        outcome, _ = run([dict(GOOD, finish_reason="length")])
        self.assertEqual("ubrukelig", outcome["utfall"])

    def test_baseline_never_retries(self):
        outcome, _ = run([limited(), GOOD], robust.BASELINE)
        self.assertEqual("feilet", outcome["utfall"])

    def test_gate_limits_calls_in_flight(self):
        active, peak, lock = [0], [0], threading.Lock()

        def send(key, payload):
            with lock:
                active[0] += 1
                peak[0] = max(peak[0], active[0])
            time.sleep(0.02)
            with lock:
                active[0] -= 1
            return GOOD

        gate = threading.BoundedSemaphore(robust.POLICY["samtidige"])
        threads = [threading.Thread(target=robust.call_with_policy,
                                    args=("k", {}, CASE, robust.POLICY, gate, random.Random(1)),
                                    kwargs={"send": send}) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(robust.POLICY["samtidige"], peak[0])


class ReportTests(unittest.TestCase):
    def test_summary_counts_outcomes_and_wave_time(self):
        outcomes = [
            {"utfall": "ok", "forsok": [{"status": 429, "headers": {"retry-after": "2"}}, {"status": 200, "headers": {}}],
             "sekunder": 2.5, "usage": {"cost": 0.0001}, "bolge": 0, "ferdig_etter_bolgestart_s": 2.6},
            {"utfall": "feilet", "forsok": [{"status": 402, "headers": {}}], "sekunder": 0.1, "usage": None,
             "bolge": 1, "ferdig_etter_bolgestart_s": 0.2}]
        s = robust.summarize(outcomes)
        self.assertEqual((2, 1, 1, 1, 1), (s["kall"], s["ok"], s["feilet"], s["http_429"], s["andre_feil"]))
        self.assertEqual(2.6, s["bolge_ferdig_maks_s"])
        self.assertEqual(["2"], s["retry_after_sett"])

    def test_dry_run_reads_no_key(self):
        with patch.object(robust.base, "configuration", side_effect=AssertionError("key read")), \
                patch("sys.argv", ["modelltest_robusthet.py"]):
            self.assertEqual(0, robust.main())

    def test_scenarios_cover_the_planned_load(self):
        counts = {name: sum(n for _, _, n in waves) for name, waves in robust.SCENARIOS.items()}
        self.assertEqual({"S1_en_vakt": 10, "S2_to_vakter_samtidig": 20, "S3_fem_vakter_5s_mellom": 50,
                          "S4_tre_vakter_gjenapnet": 60, "S5_tolk_30_preferanser": 30}, counts)


if __name__ == "__main__":
    unittest.main()
