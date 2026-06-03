import random

import automaton_parser as parser


class GrammarError(Exception):
    pass


class UndefinedStartSymbolError(GrammarError):
    pass


class UndefinedProductionRulesError(GrammarError):
    pass


class InvalidSymbolError(GrammarError):
    pass


class InvalidProductionError(GrammarError):
    pass


def parseRules(ruleLines):
    rules = {}

    for line in ruleLines:
        if "->" not in line:
            raise InvalidProductionError(f"Invalid production rule: {line}")

        leftSide, rightSide = line.split("->", 1)
        leftSide = leftSide.strip()
        rightSide = rightSide.strip()

        if leftSide not in rules:
            rules[leftSide] = []

        rules[leftSide].append(rightSide.split())

    return rules


def parseFile(inputGrammarFile):
    sections = parser.parse_sections(inputGrammarFile)

    nonterminals = sections.get("Nonterminals", [])
    terminals = sections.get("Terminals", [])
    variables = sections.get("Variables", [])
    rules = parseRules(sections.get("Rules", []))

    startSection = sections.get("Start", [])
    if len(startSection) == 0:
        start = "None"
    elif len(startSection) == 1:
        start = startSection[0]
    else:
        raise UndefinedStartSymbolError("A grammar can only have one start symbol")

    grammar = nonterminals, terminals, variables, rules, start
    if not isGrammarValid(grammar):
        return False
    return grammar


def isGrammarValid(grammar):
    nonterminals, terminals, variables, rules, start = grammar

    if len(nonterminals) == 0:
        raise InvalidSymbolError("Nonterminals are not defined")

    if len(terminals) == 0:
        raise InvalidSymbolError("Terminals are not defined")

    if start == "None":
        raise UndefinedStartSymbolError("Start symbol is not defined")

    if start not in nonterminals:
        raise InvalidSymbolError(f"Start symbol {start} is not defined in the grammar nonterminals")

    if len(rules) == 0:
        raise UndefinedProductionRulesError("Production rules are not defined")

    for leftSide in rules:
        if leftSide not in nonterminals:
            raise InvalidProductionError(f"Left side symbol {leftSide} is not defined in the grammar nonterminals")

        for production in rules[leftSide]:
            if len(production) == 0:
                raise InvalidProductionError(f"Production for {leftSide} is empty")

            for symbol in production:
                if symbol not in nonterminals and symbol not in terminals and symbol not in variables:
                    raise InvalidSymbolError(f"Symbol {symbol} is not defined in the grammar")

    return True


def printGrammarDataStructures(grammar):
    nonterminals, terminals, variables, rules, start = grammar

    print(f"Nonterminals : {nonterminals}")
    print(f"Terminals : {terminals}")
    print(f"Variables : {variables}")
    print(f"Rules : {rules}")
    print(f"Start symbol : {start}")


def generateFromSymbol(grammar, startSymbol, substitutions=None, maxDepth=20):
    nonterminals, terminals, variables, rules, start = grammar

    if substitutions is None:
        substitutions = {}

    if startSymbol not in nonterminals:
        raise InvalidSymbolError(f"Symbol {startSymbol} is not a nonterminal in the grammar")

    generatedTokens = expandSymbol(startSymbol, rules, nonterminals, terminals, variables, substitutions, maxDepth)
    return formatGeneratedTokens(generatedTokens)


def expandSymbol(currentSymbol, rules, nonterminals, terminals, variables, substitutions, depthLeft):
    if depthLeft < 0:
        raise GrammarError("Maximum grammar expansion depth exceeded")

    if currentSymbol in terminals:
        return [currentSymbol]

    if currentSymbol in variables:
        return [substitutions.get(currentSymbol, currentSymbol.lower())]

    if currentSymbol not in rules:
        raise InvalidProductionError(f"No production rule found for nonterminal {currentSymbol}")

    production = random.choice(rules[currentSymbol])
    expandedTokens = []

    for symbol in production:
        expandedTokens.extend(expandSymbol(symbol, rules, nonterminals, terminals, variables, substitutions, depthLeft - 1))

    return expandedTokens


def formatGeneratedTokens(tokens):
    if len(tokens) == 0:
        return ""

    sentence = " ".join(tokens)
    for punctuation in [" ?", " .", " !", " ,"]:
        sentence = sentence.replace(punctuation, punctuation[-1])

    return sentence
