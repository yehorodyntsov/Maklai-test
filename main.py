from fastapi import FastAPI
import itertools
import re
import nltk
from nltk.tree import *

app = FastAPI()

"""
Creates an API in Python, which implements a single endpoint that accepts syntactic input
tree of the English text and returns its paraphrased versions:
"""
@app.get("/paraphrase")

async def root(tree: str, limit: int = 20):
    paraphrases = create_paraphrases(tree, limit)

    return {"paraphrases": paraphrases.get("paraphrases")}

def find_nps(subtree):
    """

    :param subtree: subtree of nltk tree
    :return: positions of NP nodes that are divided with CC or (, ,)
    """
    tree = list(subtree)
    result = []
    index = 0
    while index < len(tree):
        if isinstance(tree[index], nltk.Tree) and tree[index].label() == "NP":
            first_np_index = index
            while index < len(tree) - 2 and (tree[index + 1].label() == "CC" or tree[index + 1].label() == ","):
                if tree[index + 2].label() == "NP":
                    if not result:
                        first_np = tree[first_np_index]
                        result.append(first_np.treeposition())
                    second_np = tree[index + 2]
                    result.append(second_np.treeposition())
                    index += 2
                    break
                index += 1
        index += 1
        return result


def create_tree(old_nps, new_nps, parse_tree):
    """
    Creates tree with rearranged nodes
    :param old_nps: positions of nodes of initial tree
    :param new_nps: positions of nodes of changed tree
    :param parse_tree: initial tree
    :return:tree with rearranged nodes
    """
    result = parse_tree.copy()
    for i, positions in enumerate(old_nps):
        for j, position in enumerate(positions):
            result[new_nps[i][j]] = parse_tree[old_nps[i][j]].copy()
    return result


def create_paraphrases(tree, limit):
    """
    Finds in the text all NPs separated by comma or CC
    Generate variants of permutations of these daughter NPs with each other.
    :param tree: initial tree
    :param limit: max created trees
    :return: dictionary of created trees
    """
    parse_tree = ParentedTree.fromstring(tree)
    subtrs = parse_tree.subtrees()
    nps_positions = []

    for subtree_index, subtree in enumerate(subtrs):
        lst = find_nps(subtree)
        if len(lst) > 0:
            nps_positions.append(lst)

    permutations = []
    for i in nps_positions:
        permutations.append(list(itertools.permutations(i)))

    trees_variations = []
    for combination in itertools.islice(itertools.product(*permutations),limit):
        trees_variations.append(combination)

    trees = []
    for i in trees_variations:
        #tree_str = re.sub(r'\s+', ' ', str(create_tree(nps_positions, i, parse_tree))).strip()
        tree_str = str(create_tree(nps_positions, i, parse_tree))
        trees.append(tree_str)

    answer = {"paraphrases": []}
    for tree in trees:
        answer["paraphrases"].append({"tree": str(tree)})
    return answer
