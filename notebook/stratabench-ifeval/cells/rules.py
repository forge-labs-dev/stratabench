# @name Rule checkers (IFEval instruction subset)
#
# IFEval ships ~25 rule types. v1 implements the 16 most common ones
# inline so reproducers can read every check in this file. Prompts that
# require uncovered rules are *skipped* (not penalized) at score time
# and the coverage percentage is reported alongside the score.
#
# Each checker takes (response, kwargs) and returns True / False. The
# kwargs dict comes verbatim from the dataset row — IFEval's reference
# impl pulls from the same field names. Citations are inline at the
# top of each function so a reader can compare against the upstream
# ``instructions.py`` if a number ever drifts.
#
# Citation comment for the audit trail:
#   IFEval reference: github.com/google-research/google-research/tree/master/instruction_following_eval
#   lm-eval task reference: lm_eval/tasks/ifeval/ifeval.yaml

from __future__ import annotations

import json
import re
from typing import Callable

# Sentence splitter that's IFEval-faithful: split on '. ', '! ', '? '
# while leaving abbreviations alone is hard; the reference impl uses
# nltk.sent_tokenize. We approximate with a regex so reproducers can
# read the rule without an nltk dependency. Trailing-punctuation +
# whitespace boundary catches the common cases; quirky abbreviations
# may inflate sentence counts slightly. Documented as a v1 caveat.
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"\b\w+\b")
_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")


def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text)


def _sentences(text: str) -> list[str]:
    return [s for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s]


def _paragraphs(text: str) -> list[str]:
    return [p for p in _PARAGRAPH_SPLIT_RE.split(text.strip()) if p]


def _relation(value: int, target: int, relation: str) -> bool:
    return value <= target if relation == "less than" else value >= target


# --- Keywords ------------------------------------------------------------
def keywords_existence(response: str, kw: dict) -> bool:
    keywords = kw.get("keywords", [])
    return all(k.lower() in response.lower() for k in keywords)


def keywords_forbidden(response: str, kw: dict) -> bool:
    forbidden = kw.get("forbidden_words", [])
    return all(f.lower() not in response.lower() for f in forbidden)


def keywords_frequency(response: str, kw: dict) -> bool:
    keyword = kw["keyword"]
    target = int(kw["frequency"])
    relation = kw.get("relation", "at least")
    count = len(re.findall(re.escape(keyword), response, flags=re.IGNORECASE))
    return _relation(count, target, relation)


def keywords_letter_frequency(response: str, kw: dict) -> bool:
    letter = kw["letter"].lower()
    target = int(kw["let_frequency"])
    relation = kw.get("let_relation", "at least")
    count = response.lower().count(letter)
    return _relation(count, target, relation)


# --- Length constraints --------------------------------------------------
def length_number_words(response: str, kw: dict) -> bool:
    target = int(kw["num_words"])
    relation = kw.get("relation", "at least")
    return _relation(len(_words(response)), target, relation)


def length_number_sentences(response: str, kw: dict) -> bool:
    target = int(kw["num_sentences"])
    relation = kw.get("relation", "at least")
    return _relation(len(_sentences(response)), target, relation)


def length_number_paragraphs(response: str, kw: dict) -> bool:
    target = int(kw["num_paragraphs"])
    return len(_paragraphs(response)) == target


def length_nth_paragraph_first_word(response: str, kw: dict) -> bool:
    nth = int(kw["nth_paragraph"])
    expected = kw["first_word"].strip().lower()
    paragraphs = _paragraphs(response)
    if nth < 1 or nth > len(paragraphs):
        return False
    first_word = paragraphs[nth - 1].split()
    return bool(first_word) and first_word[0].lower().strip(".,;:!?\"'") == expected


# --- Detectable format ---------------------------------------------------
def detectable_format_json(response: str, kw: dict) -> bool:
    """Strip a fenced ```json``` block if present, else parse the whole."""
    body = response.strip()
    fence = re.search(r"```(?:json)?\s*\n(.*?)```", body, flags=re.DOTALL)
    if fence:
        body = fence.group(1)
    try:
        json.loads(body)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def detectable_format_number_bullet_lists(response: str, kw: dict) -> bool:
    target = int(kw["num_bullets"])
    bullets = re.findall(r"(?m)^\s*[*-]\s+\S", response)
    return len(bullets) == target


def detectable_format_title(response: str, kw: dict) -> bool:
    return re.search(r"<<.+?>>", response) is not None


def detectable_format_constrained_response(response: str, kw: dict) -> bool:
    options = kw["response_options"]
    stripped = response.strip()
    return any(stripped == option for option in options)


def detectable_format_multiple_sections(response: str, kw: dict) -> bool:
    splitter = kw["section_spliter"]
    target = int(kw["num_sections"])
    # Sections are separated by lines starting with the splitter token.
    matches = re.findall(rf"(?m)^{re.escape(splitter)}\s+\d+", response)
    return len(matches) == target


# --- Start/end -----------------------------------------------------------
def startend_end_checker(response: str, kw: dict) -> bool:
    end_phrase = kw["end_phrase"].strip()
    return response.strip().rstrip(".!?\"'").endswith(end_phrase.rstrip(".!?\"'"))


def startend_quotation(response: str, kw: dict) -> bool:
    s = response.strip()
    return len(s) >= 2 and s[0] in '"“' and s[-1] in '"”'


# --- Change case ---------------------------------------------------------
def change_case_english_capital(response: str, kw: dict) -> bool:
    letters = [c for c in response if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def change_case_english_lowercase(response: str, kw: dict) -> bool:
    letters = [c for c in response if c.isalpha()]
    return bool(letters) and all(c.islower() for c in letters)


# --- Punctuation ---------------------------------------------------------
def punctuation_no_comma(response: str, kw: dict) -> bool:
    return "," not in response


# --- Registry ------------------------------------------------------------
RULES: dict[str, Callable[[str, dict], bool]] = {
    "keywords:existence": keywords_existence,
    "keywords:forbidden_words": keywords_forbidden,
    "keywords:frequency": keywords_frequency,
    "keywords:letter_frequency": keywords_letter_frequency,
    "length_constraints:number_words": length_number_words,
    "length_constraints:number_sentences": length_number_sentences,
    "length_constraints:number_paragraphs": length_number_paragraphs,
    "length_constraints:nth_paragraph_first_word": length_nth_paragraph_first_word,
    "detectable_format:json_format": detectable_format_json,
    "detectable_format:number_bullet_lists": detectable_format_number_bullet_lists,
    "detectable_format:title": detectable_format_title,
    "detectable_format:constrained_response": detectable_format_constrained_response,
    "detectable_format:multiple_sections": detectable_format_multiple_sections,
    "startend:end_checker": startend_end_checker,
    "startend:quotation": startend_quotation,
    "change_case:english_capital": change_case_english_capital,
    "change_case:english_lowercase": change_case_english_lowercase,
    "punctuation:no_comma": punctuation_no_comma,
}
