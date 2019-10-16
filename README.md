## Install requirements

pip install -r requirements.txt

## How to use

You can use run.py to run the code, inside run.py there are instructions on how to tinker with the parameters

## Genetic algorithm

The genetic algorithm is divided into 3 main .py files
    * genetic_algorithm.py - the algorithm itself
    * individuals.py
    * population.py

There is also a network.py file which encapsulates all graph related processes we need.

## Creating new models

If one is interested in creating new models to try out please replace \models\places with a new list of places.
A single entry in the place file is of the form "<place>,<country>". Finally run \models\geo.py to generate a geographically correct model of the places,
the edges are however chosen with a nearest neighbour criterion.