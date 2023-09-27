import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S | S Conj VP 
NP -> N | AP NP | N PP | Det NoDetNP
NoDetNP -> N | AP NP | N PP
PP -> P NP
AP -> Adj | Adj NP
VP -> V | V NP | V PP | VA NP | V PP Adv | VA
VA -> Adv V | V Adv
"""


grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    sentence = nltk.word_tokenize(sentence)
    sentence = [w.lower() for w in sentence if w.isalpha()]
    return sentence


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    np_subtrees = list(tree.subtrees(filter=lambda t: filter_trees(t)))
    to_remove = []

    for i in range(len(np_subtrees)):
        for j in range(len(np_subtrees)):
            # if the trees are the same object continue iteration
            if i == j:
                continue
            # if leaves of a subtree[i] are a subset of subtree[j] remove the subtree[i] 
            if set(np_subtrees[i].leaves()).issubset(set(np_subtrees[j].leaves())):
                to_remove.append(np_subtrees[i])
                
    # remove duplicates (str conversion so its hashable)
    to_remove = set([str(tree) for tree in to_remove])

    # revert strings back to trees
    to_remove = [nltk.Tree.fromstring(tree) for tree in to_remove]

    for sub in to_remove:
        # remove the marked trees
        np_subtrees.remove(sub)
    return np_subtrees


def filter_trees(tree):
    """
    This function filters out all trees that are not noun phrases
    and contain more than one noun in its structure
    """
    labels = [sub.label() for sub in tree.subtrees()]

    # label at index 0 is a label of the tree because the tree itself is its own subtree too
    child_labels = labels[1:]
    nouns = 0
    for label in child_labels:
        if label == "N":
            nouns += 1
    if nouns > 1:
        return False
    if tree.label() == "NP":
        return True


if __name__ == "__main__":
    main()
