# TTRP (Truck and Trailer Problem)

> A tabu search method for the TTRP.

In the truck and trailer routing problem (TTRP) a fleet of trucks and trailers serves a set of customers.
Some customers with accessibility constraints must be served just by truck, while others can be served
either by truck or by a complete vehicle (a truck pulling a trailer). This problem originally introduced by Chao, it's a variant of the vehicle routing problem (VRP).

*note:* Cplex needed

Dataset sources [here](http://web.ntust.edu.tw/~vincent/ttrp/).

**Main part**

- A relaxed assignment problem (solve by Cplex)

- Cheapest insertion heuristics (a TSP construction heuristics) and other construction heuristics for route construction

- Descent improvement which have three move strategy:
    - one-point exchange
    - two-point swap
    - sub-tour root-refining

- 2-opt algorithm

- Tabu search， including:
    - objective based restriction
    - history movement restriction
    - intensification & diversification stages

⏳ still coding