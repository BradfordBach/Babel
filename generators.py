import inflect
import random


def store_naming_list(location):
    word_list = []
    with open(location) as inputfile:
        for line in inputfile:
            word_list.append(line.strip().lower())
    return word_list


def generate_animal_hex():
    p = inflect.engine()
    adjective_list = store_naming_list('Data/adjectives.txt')
    animal_list = store_naming_list('Data/animals.txt')
    if random.randint(0, 1) == 1:
        number_of = str(random.randint(2, 10000))
        hex_name = number_of + random.choice(adjective_list) + random.choice(adjective_list) + p.plural(
            random.choice(animal_list))
    else:
        hex_name = random.choice(adjective_list) + random.choice(adjective_list) + random.choice(animal_list)

    return hex_name
