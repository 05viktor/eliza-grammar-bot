import random
import re

import automaton_parser as parser
import Grammar as grammarModule


class PatternError(Exception):
    pass


def parsePatterns(patternLines):
    patterns = []

    for line in patternLines:
        parts = [part.strip() for part in line.split("=>")]
        if len(parts) < 2 or len(parts) > 3:
            raise PatternError(f"Invalid pattern definition: {line}")

        patternText = parts[0]
        targetSymbol = parts[1]
        capturedVariable = None
        if len(parts) == 3:
            capturedVariable = parts[2]

        patterns.append({
            "pattern": patternText,
            "target": targetSymbol,
            "variable": capturedVariable,
        })

    return patterns


def parseReflections(reflectionLines):
    reflections = {}

    for line in reflectionLines:
        if "=>" not in line:
            raise PatternError(f"Invalid reflection rule: {line}")

        source, destination = line.split("=>", 1)
        reflections[source.strip().lower()] = destination.strip().lower()

    return reflections


def parsePatternFile(inputPatternFile):
    sections = parser.parse_sections(inputPatternFile)
    patterns = parsePatterns(sections.get("Patterns", []))
    reflections = parseReflections(sections.get("Reflections", []))
    quits = sections.get("Quit Words", ["bye", "quit", "exit"])
    return patterns, reflections, quits


def normalizeInput(userInput):
    loweredInput = userInput.lower().strip()
    loweredInput = re.sub(r"[^\w\s']", " ", loweredInput)
    loweredInput = re.sub(r"\s+", " ", loweredInput).strip()
    return loweredInput


def reflectFragment(fragment, reflections):
    reflectedTokens = []

    for token in fragment.split():
        reflectedTokens.append(reflections.get(token, token))

    return " ".join(reflectedTokens).strip()


def tokenizePattern(patternText):
    return patternText.lower().split()


def matchPattern(patternText, normalizedInput):
    patternTokens = tokenizePattern(patternText)
    inputTokens = normalizedInput.split()

    return matchPatternTokens(patternTokens, inputTokens)


def matchPatternTokens(patternTokens, inputTokens):
    if len(patternTokens) == 0:
        if len(inputTokens) == 0:
            return True, []
        return False, []

    currentPatternToken = patternTokens[0]

    if currentPatternToken == "*":
        if len(patternTokens) == 1:
            return True, [" ".join(inputTokens).strip()]

        for splitIndex in range(len(inputTokens) + 1):
            matched, captures = matchPatternTokens(patternTokens[1:], inputTokens[splitIndex:])
            if matched:
                capturedFragment = " ".join(inputTokens[:splitIndex]).strip()
                return True, [capturedFragment] + captures
        return False, []

    if len(inputTokens) == 0:
        return False, []

    if currentPatternToken != inputTokens[0]:
        return False, []

    return matchPatternTokens(patternTokens[1:], inputTokens[1:])


class ElizaBot:
    def __init__(self, grammar, patterns, reflections, quitWords):
        self.grammar = grammar
        self.patterns = patterns
        self.reflections = reflections
        self.quitWords = set(word.lower() for word in quitWords)

    def wantsToQuit(self, userInput):
        return normalizeInput(userInput) in self.quitWords

    def respond(self, userInput):
        normalizedInput = normalizeInput(userInput)
        if normalizedInput == "":
            return "Please tell me something."

        for patternData in self.patterns:
            matched, captures = matchPattern(patternData["pattern"], normalizedInput)
            if not matched:
                continue

            substitutions = {}
            if patternData["variable"] is not None and len(captures) > 0:
                substitutions[patternData["variable"]] = reflectFragment(captures[0], self.reflections)

            try:
                return grammarModule.generateFromSymbol(
                    self.grammar,
                    patternData["target"],
                    substitutions,
                )
            except grammarModule.GrammarError:
                continue

        fallbackResponses = [
            "Please go on.",
            "Tell me more.",
            "Why do you say that?",
        ]
        return random.choice(fallbackResponses)
