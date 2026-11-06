"""Kontroll av at Codex (.agents/skills) og Claude Code (.claude/skills) har samme skills.

AGENTS.md krever at en endring i den ene mappen speiles i den andre. Linjeskift
ignoreres, fordi .agents-kopien har CRLF i arbeidstreet på Windows. Bare sporede
filer sammenlignes, så lokale filer som __pycache__ og .DS_Store gir ikke feil.
"""

from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent
CODEX = ".agents/skills"
CLAUDE = ".claude/skills"
# Vedtatte unntak (AGENTS.md, «Sesjonslogg»): Codex-filen er bare metadata og en henvisning.
POINTERS = {"sesjonslogg/SKILL.md"}


def tracked(folder):
    out = subprocess.run(["git", "ls-files", "-z", "--", folder], cwd=ROOT,
                         capture_output=True, check=True).stdout.decode("utf-8")
    return {path[len(folder) + 1:] for path in out.split("\0") if path}


def content(folder, path):
    return (ROOT / folder / path).read_bytes().replace(b"\r\n", b"\n")


class SkillMirror(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.codex, cls.claude = tracked(CODEX), tracked(CLAUDE)

    def test_same_files_in_both_folders(self):
        self.assertTrue(self.claude, "Fant ingen sporede filer i .claude/skills")
        self.assertEqual([], sorted(self.claude - self.codex), "Finnes bare i .claude/skills")
        self.assertEqual([], sorted(self.codex - self.claude), "Finnes bare i .agents/skills")

    def test_same_content_except_pointers(self):
        differs = sorted(path for path in (self.codex & self.claude) - POINTERS
                         if content(CODEX, path) != content(CLAUDE, path))
        self.assertEqual([], differs, "Ulikt innhold i .agents/skills og .claude/skills — speil endringen")

    def test_pointer_keeps_name_and_links_the_claude_skill(self):
        name = re.compile(r"^name: *(\S+)", re.M)
        for path in POINTERS:
            with self.subTest(path=path):
                codex = content(CODEX, path).decode("utf-8")
                claude = content(CLAUDE, path).decode("utf-8")
                self.assertEqual(name.search(claude).group(1), name.search(codex).group(1))
                self.assertIn(f"{CLAUDE}/{path}", codex)


if __name__ == "__main__":
    unittest.main()
