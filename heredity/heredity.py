import csv
import itertools
import sys

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
    zero_genes = set(people.keys()).difference(one_gene).difference(two_genes)
    not_have_trait = set(people.keys()).difference(have_trait)
    chances = []


    for person in zero_genes:
        mom = people[person]['mother']
        momCount = (
            0 if mom in zero_genes else
            1 if mom in one_gene else
            2
        )
        
        dad = people[person]['father']
        dadCount = (
            0 if dad in zero_genes else
            1 if dad in one_gene else
            2
        )
        if people[person]['mother'] is None:
            chances.append(PROBS["gene"][0])
        else:
            chances.append(getChance(people, 0, person, momCount,dadCount))
    
    for person in one_gene:
        mom = people[person]['mother']
        momCount = (
            0 if mom in zero_genes else
            1 if mom in one_gene else
            2
        )
        
        dad = people[person]['father']
        dadCount = (
            0 if dad in zero_genes else
            1 if dad in one_gene else
            2
        )
        if people[person]['mother'] is None:
            chances.append(PROBS["gene"][1])
        else:
            chances.append(getChance(people, 1, person, momCount,dadCount))
    
    for person in two_genes:
        mom = people[person]['mother']
        momCount = (
            0 if mom in zero_genes else
            1 if mom in one_gene else
            2
        )
        
        dad = people[person]['father']
        dadCount = (
            0 if dad in zero_genes else
            1 if dad in one_gene else
            2
        )
        if people[person]['mother'] is None:
            chances.append(PROBS["gene"][2])
        else:
            chances.append(getChance(people, 2, person, momCount,dadCount))
    
    for person in have_trait:
        personGenes = (
            0 if person in zero_genes else
            1 if person in one_gene else
            2
        )
        chances.append(PROBS["trait"][personGenes][True])
    
    for person in not_have_trait:
        personGenes = (
            0 if person in zero_genes else
            1 if person in one_gene else 
            2
        )
        chances.append(PROBS["trait"][personGenes][False])

    totalP = 1
    for elem in chances:
        totalP*=elem
    return totalP
        
def getChance(people, geneCount, person, momGenes,dadGenes):
    if momGenes is None:
            return PROBS["gene"][geneCount]
    if geneCount == 0:
        if momGenes == 0:
            momChance = 0.99
        elif momGenes == 1:
            momChance = 0.5
        else:
            momChance = 0.01
        if dadGenes == 0:
            dadChance = 0.99
        elif dadGenes == 1:
            dadChance = 0.5
        else:
            dadChance = 0.01
        return momChance * dadChance

    elif geneCount == 1:
        if momGenes == 0:
            momChance0 = 0.99
            momChance1 = 0.01
        elif momGenes == 1:
            momChance0 = 0.5
            momChance1 = 0.5
        else:
            momChance0 = 0.01
            momChance1 = 0.99
        if dadGenes == 0:
            dadChance0 = 0.99
            dadChance1 = 0.01
        elif dadGenes == 1:
            dadChance0 = 0.5
            dadChance1 = 0.5
        else:
            dadChance0 = 0.01
            dadChance1 = 0.99
        return momChance0*dadChance1 + momChance1*dadChance0
    else:
        if momGenes == 0:
            momChance = 0.01
        elif momGenes == 1:
            momChance = 0.5
        else:
            momChance = 0.99
        if dadGenes == 0:
            dadChance = 0.01
        elif dadGenes == 1:
            dadChance = 0.5
        else:
            dadChance = 0.99
        return momChance * dadChance

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1]+=p
        elif person in two_genes:
            probabilities[person]["gene"][2]+=p
        else:
            probabilities[person]["gene"][0]+=p
            
        if person in have_trait:
            probabilities[person]["trait"][True]+=p
        else:
            probabilities[person]["trait"][False]+=p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities.keys():
        genesum = 0
        traitsum = 0
        for prob in probabilities[person]["gene"].keys():
            genesum+=probabilities[person]["gene"][prob]
        for prob in probabilities[person]["trait"].keys():
            traitsum+=probabilities[person]["trait"][prob]
        genefactor = 1/genesum
        traitfactor = 1/traitsum
        for prob in probabilities[person]["gene"].keys():
            probabilities[person]["gene"][prob]*=genefactor
        for prob in probabilities[person]["trait"].keys():
            probabilities[person]["trait"][prob]*=traitfactor



if __name__ == "__main__":
    main()
