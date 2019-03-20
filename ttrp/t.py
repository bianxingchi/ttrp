#!/usr/bin/env python
# coding=utf-8

# class Assignment:
#     def __init__(self):
#         self.truck_num = 5
#         self.trailer_num = 3

#     def one(self):
#         dists_di = [0, 1, 2]
#         # return dists_di

#     def two(self):
#         di = self.one()[0]
#         # return di

# A = Assignment()
# print(A.two())

# from readdata import ReadData
# from model import Model
# from math import hypot, ceil
# import random
# from operator import itemgetter

# class Construction:
#     def __init__(self):
#         self.AM = Model().solve() # return the values of the model, list
#         self.one = ReadData("TTRP_01.txt")
#         self.truck_num = 5
#         self.trailer_num = 3

#     # get the five tours
#     def get_tours(self):
#         seqs = []
#         for i in range(self.truck_num):
#             seq = range(i, self.one.customer_num * self.truck_num, self.truck_num)
#             seqs.append(seq)
#         tours = []
#         for seq in seqs:
#             tour = []
#             for index in seq:
#                 if self.AM[index] > 0.5:
#                     tour.append(ceil((index + 1) / 5))
#             tours.append(tour - 1)
#         return tours

#     def compute_dist(self, i, j):
#         for node in self.one.get_locations():
#             # print(node)
#             if i == node[0]:
#                 cord_i = node[1]
#             if j == node[0]:
#                 cord_j = node[1]
#         dist_ij = hypot(float(cord_i[0]) - float(cord_j[0]),
#                         float(cord_i[1]) - float(cord_j[1]))
#         return dist_ij
    
#     def closest_neighbor(self, current_tour, node):
#         dists = {}
#         for cus in current_tour:
#             if cus == node:
#                 continue
#             dist = self.compute_dist(node, cus)
#             dists.update({cus: dist})
#         return sorted(dists.items(), key=itemgetter(1))[0][0]

# a = Construction()
# print(a.closest_neighbor([22, 3, 1], 22)) # 3
# print(a.compute_dist(1, 22))
# print(a.compute_dist(3, 22))

from readdata import ReadData
from construction import Construction

class Descent(Construction):
    def pv(self):
        return self.pure_truck()
    
    def opd(self):
        tr = self.pure_truck()
        pv = self.pure_vehicle()
        cv = self.all_complete_tour()
        main_tours, sub_tours = [], []
        for seqs in cv:
            main_tours.append(seqs[0])
            sub_tours.append(seqs[1]) # this will be a list of list of list
        # print(tr + pv + main_tours + sub_tours)
        print(sub_tours)
        sss = [[[49, 15, 10, 0, 45, 8], [0, 0, 0]], [[36, 4, 11, 16]], [[41, 46, 40, 18]]]
        ss = []
        for tour in sss:
            ss += tour
        print(ss)
        return "here"
    
    def ahah(self):
        a = [1, 2, 3]
        if a in [0]:
            return "yes1"
        elif a in [1]:
            return "yes2"
        elif a in [[1, 2, 3], 4]:
            return "yes3"

    def lala(self):
        print(self.pv())
        print(self.pv())

if __name__ == "__main__":
    d = Descent()
    # print(d.opd())
    print(d.lala())    