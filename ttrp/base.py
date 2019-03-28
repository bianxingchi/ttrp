#!/usr/bin/env python
# coding=utf-8

# some base algorithms for usage
class BaseAlgorithms:
    # find the closest neighbor to a given node in the tour
    def closest_neighbor(self, current_tour, node):
        dists = {}
        for cus in current_tour:
            if cus == node:
                continue
            dist = self.compute_dist(node, cus)
            dists.update({cus: dist})
        return sorted(dists.items(), key=itemgetter(1))[0][0]

    
