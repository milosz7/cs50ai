import csv
import itertools
import sys
import math

NO_GENES = 0
ONE_GENE = 1
TWO_GENES = 2

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    final_probs = []

    for person in people:
        person_probs = []
        trait = person in have_trait
        child = people[person]["mother"] is not None
        genes_amt = assign_gene_amount(person, one_gene, two_genes)

        if child:
            mother = people[person]["mother"]
            father = people[person]["father"]
            mother_genes_amt = assign_gene_amount(mother, one_gene, two_genes)
            father_genes_amt = assign_gene_amount(father, one_gene, two_genes)

            if genes_amt == NO_GENES:
                mother_probs = pass_gene_probability(
                    mother_genes_amt, pass_proba=False)
                father_probs = pass_gene_probability(
                    father_genes_amt, pass_proba=False)

                person_probs.append((mother_probs * father_probs))

            if genes_amt == ONE_GENE:
                # There are two possible cases: either mother gives and father does not
                # or the father gives and the mother does not, probability of passing the
                # gene is equal to sum of these cases
                case1 = pass_gene_probability(mother_genes_amt)
                case1 *= pass_gene_probability(father_genes_amt,
                                               pass_proba=False)
                case2 = pass_gene_probability(mother_genes_amt,
                                              pass_proba=False)
                case2 *= pass_gene_probability(father_genes_amt)

                person_probs.append((case1 + case2))

            if genes_amt == TWO_GENES:
                mother_probs = pass_gene_probability(mother_genes_amt)
                father_probs = pass_gene_probability(father_genes_amt)

                person_probs.append((mother_probs * father_probs))

            person_probs.append(PROBS["trait"][genes_amt][trait])

        if not child:
            person_probs += extract_probs(genes_amt, trait)

        person_joint_proba = math.prod(person_probs)
        final_probs.append(person_joint_proba)

    final_joint_proba = math.prod(final_probs)
    return final_joint_proba


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        genes_amt = assign_gene_amount(person, one_gene, two_genes)
        has_trait = person in have_trait
        probabilities[person]["gene"][genes_amt] += p
        probabilities[person]["trait"][has_trait] += p
    

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        to_normalize = probabilities[person].keys()

        for d1_key in to_normalize:
            proba_sum = sum(list(probabilities[person][d1_key].values()))
            d2_keys = probabilities[person][d1_key].keys()

            for d2_key in d2_keys:
                probabilities[person][d1_key][d2_key] /= proba_sum


def extract_probs(n_copies, trait):
    return [PROBS["gene"][n_copies], PROBS["trait"][n_copies][trait]]


def assign_gene_amount(person, one_gene, two_genes):
    if person in one_gene:
        return ONE_GENE
    if person in two_genes:
        return TWO_GENES
    return NO_GENES


def pass_gene_probability(n_copies, pass_proba=True):
    # here we multiply by 0.5 because each gene copy gives 50% chance to pass it
    if n_copies == ONE_GENE:
        return 0.5
    if pass_proba:
        return abs(n_copies * 0.5 + PROBS["mutation"])
    if not pass_proba:
        return abs(1 - n_copies * 0.5 + PROBS["mutation"])


if __name__ == "__main__":
    main()
