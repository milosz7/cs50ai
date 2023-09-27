import os
import random
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probs = dict()
    pages = list(corpus.keys())
    random_choice_factor = float(
        f'{(1 - damping_factor) / len(corpus.keys()):.4f}')
    current_links = corpus[page]

    if len(current_links) == 0:
        for link in pages:
            probs[link] = 1 / len(pages)
    else:
        for link in pages:
            probs[link] = random_choice_factor
            if link in current_links:
                probs[link] += damping_factor * (1 / len(current_links))
    return probs


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    ranks = {page: 0 for page in pages}
    start_page = random.choice(pages)
    ranks[start_page] += 1
    probs = transition_model(corpus, start_page, damping_factor).items()

    for _ in range(n):
        weights = [pair[1] for pair in probs]
        elements = [pair[0] for pair in probs]
        next_page = random.choices(elements, weights, k=1)[0]
        ranks[next_page] += 1
        probs = transition_model(corpus, next_page, damping_factor).items()

    ranks = {key: (value / n) for (key, value) in ranks.items()}
    return ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    starting_rank = 1 / len(pages)
    ranks = {page: starting_rank for page in pages}
    diffs = {page: math.inf for page in pages}
    converged = False
    DIFF_THRESHOLD = 0.001

    for page in pages:
        if len(corpus[page]) == 0:
            corpus[page] = set(pages)

    while not converged:
        for page in pages:
            old_rank = ranks[page]
            links_to = [link for link in corpus.keys() if page in corpus[link]]
            sum = 0

            if len(links_to) == 0:
                links_to = pages

            for link in links_to:
                num_links = len(corpus[link])
                sum += ranks[link] / (num_links)

            new_rank = (1 - damping_factor) / len(pages) + damping_factor * sum
            ranks[page] = new_rank
            page_diff = abs(old_rank - new_rank)

            if diffs[page] > page_diff:
                diffs[page] = page_diff

            converged = True
            for diff in diffs.values():
                if diff > DIFF_THRESHOLD:
                    converged = False
    return ranks


if __name__ == "__main__":
    main()
