import os
import sys

import ElizaBot as botModule
import Grammar as grammarModule


class GrammarFileNotFoundError(Exception):
    pass


class PatternFileNotFoundError(Exception):
    pass


class DirectoryNotFoundError(Exception):
    pass


def changeDirectory(directoryPath):
    if os.path.isdir(directoryPath):
        os.chdir(directoryPath)
        return True
    else:
        raise DirectoryNotFoundError(f"Error: Directory '{directoryPath}' does not exist.")


grammarDefinitionFolder = "Grammar Definition Files"
patternFolder = "Pattern Files"

if len(sys.argv) == 1:
    grammarFileName = "eliza_grammar.gr"
    patternFileName = "eliza_patterns.patterns"
else:
    grammarFileName = sys.argv[1]
    if len(sys.argv) >= 3:
        patternFileName = sys.argv[2]
    else:
        patternFileName = "eliza_patterns.patterns"

try:
    changeDirectory(grammarDefinitionFolder)
    inputGrammarFile = open(grammarFileName, "r")
    os.chdir("..")
    changeDirectory(patternFolder)
    inputPatternFile = open(patternFileName, "r")
    os.chdir("..")
except FileNotFoundError as exception:
    if grammarDefinitionFolder in os.getcwd():
        raise GrammarFileNotFoundError(str(exception))
    raise PatternFileNotFoundError(str(exception))

grammar = grammarModule.parseFile(inputGrammarFile)
inputGrammarFile.close()

patterns, reflections, quitWords = botModule.parsePatternFile(inputPatternFile)
inputPatternFile.close()

eliza = botModule.ElizaBot(grammar, patterns, reflections, quitWords)

print("ELIZA: Hello. Tell me what is on your mind.")

while True:
    userInput = input("YOU: ")

    if eliza.wantsToQuit(userInput):
        print("ELIZA: Goodbye. Take care.")
        break

    print(f"ELIZA: {eliza.respond(userInput)}")
