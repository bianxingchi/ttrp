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

'''
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
'''

from construction import Construction
from copy import deepcopy

class Descent(Construction):
    def tour_demand(self, tour):
        demands = 0.0
        for cus in tour:
            if cus == 'a':
                continue
            demands += self.one.get_demands()[cus]
        return demands

    def tour_cap(self, tour, tr, pv, mt, st):
        if tour in tr:
            cap = self.one.truck_cap
            return cap
        elif tour in pv:
            cap = self.one.truck_cap + self.one.trailer_cap
            return cap
        elif tour in mt:
            cap = self.one.truck_cap + self.one.trailer_cap
            return cap
        elif tour in st:
            cap = self.one.truck_cap
            return cap
    
    def penalty(self, tour, tr, pv, mt, st):
        return max((self.tour_demand(tour) - self.tour_cap(tour, tr, pv, mt, st)), 0)

    def test(self):
        tr = self.pure_truck()
        pv = self.pure_vehicle()
        cv = self.all_complete_tour()
        main_tours, sub_tours = [], []
        for seqs in cv:
            main_tours.append(seqs[0])
            sub_tours.append(seqs[1]) # this will be a list of list of list
        split_sub_tours = []
        for tour in sub_tours:
            split_sub_tours += tour

        p1, p2, p3, p4 = 0.0, 0.0, 0.0, 0.0
        l1, l2, l3, l4 = 0.0, 0.0, 0.0, 0.0
        for i in tr:
            p1 += self.penalty(i, tr, pv, main_tours, split_sub_tours)
            l1 += self.tour_length(i)
        for i in pv:
            p2 += self.penalty(i, tr, pv, main_tours, split_sub_tours)
            l2 += self.tour_length(i)
        for i in main_tours:
            p3 += self.penalty(i, tr, pv, main_tours, split_sub_tours)
            l3 += self.tour_length(i)
        for i in split_sub_tours:
            p4 += self.penalty(i, tr, pv, main_tours, split_sub_tours)
            l4 += self.tour_length(i)
        penalty = p1 + p2 + p3 + p4
        objective = l1 + l2 + l3 + l4
        return objective, penalty

    def tpd(self, tr, pv, main_tours, split_sub_tours):
        b_tour = tr + pv + main_tours + split_sub_tours
        # print("b_tour of tpd:", b_tour)
        tr_len = len(tr)
        pv_len = len(pv)
        mt_len = len(main_tours)
        sst_len = len(split_sub_tours)
        n = 0
        for route_r in b_tour:
            n += 1
            for cusi in route_r:
                if cusi in self.connectors(main_tours, split_sub_tours) or cusi == 'a':
                    continue
                for route_s in b_tour:
                    if route_s == route_r:
                        continue
                    elif (self.one.get_types()[cusi] == 1) & (route_s in (pv or main_tours)):
                        continue
                    for cusj in route_s:
                        if cusj in self.connectors(main_tours, split_sub_tours) or cusj == 'a':
                            continue
                        elif (self.one.get_types()[cusj] == 1) & (route_s in (pv or main_tours)):
                            continue
                        penalty_r = max((self.tour_demand(route_r) +
                                     self.one.get_demands()[cusj] - 
                                     self.one.get_demands()[cusi] - 
                                     self.tour_cap(route_r, tr, pv, main_tours, split_sub_tours)), 0)
                        # theta_r = self.penalty(route_r, tr, pv, main_tours, split_sub_tours)
                        penalty_s = max((self.tour_demand(route_s) +
                                     self.one.get_demands()[cusi] - 
                                     self.one.get_demands()[cusj] - 
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                        # theta_s = self.penalty(route_s, tr, pv, main_tours, split_sub_tours)
                        if ((route_s in split_sub_tours) & (penalty_s > 0)) or ((route_r in split_sub_tours) & (penalty_r > 0)):
                            continue
                        temp_r = deepcopy(route_r)
                        temp_s = deepcopy(route_s)
                        move1 = self.move(temp_r, temp_s, cusi)
                        move2 = self.move(temp_s, temp_r, cusj) # only use move2's result, bcz it's exchange

                        cost_of_exchange = self.tour_length(move2[1]) - self.tour_length(route_r) + \
                                        self.tour_length(move2[0]) - self.tour_length(route_s)
                        
                        penalty_new_r = max((self.tour_demand(move2[1]) +
                                            self.one.get_demands()[cusj] - 
                                            self.one.get_demands()[cusi] - 
                                            self.tour_cap(route_r, tr, pv, main_tours, split_sub_tours)), 0)
                        penalty_new_s = max((self.tour_demand(move2[0]) +
                                            self.one.get_demands()[cusi] - 
                                            self.one.get_demands()[cusj] - 
                                            self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                        if ((penalty_new_r <= penalty_r) & (penalty_new_s <= penalty_s)) & \
                            (((penalty_new_r < penalty_r) or (penalty_new_s < penalty_s)) or cost_of_exchange < 0):
                        # if ((penalty_r <= theta_r) & (penalty_s <= theta_s)) & \
                        #     (((penalty_r < theta_r) or (penalty_s < theta_s)) or cost_of_exchange < 0):
                            for n, i in enumerate(b_tour):
                                if i == route_r:
                                    b_tour[n] = move2[1]
                            for n, i in enumerate(b_tour):
                                if i == route_s:
                                    b_tour[n] = move2[0]
                            if tr_len == 0:
                                tr = []
                            else:
                                tr = b_tour[:tr_len]
                            if pv_len == 0:
                                pv = []
                            else:
                                pv = b_tour[tr_len:tr_len + pv_len]
                            if mt_len == 0:
                                main_tours = []
                            else:
                                main_tours = b_tour[tr_len + pv_len:tr_len + pv_len + mt_len]
                            if sst_len == 0:
                                split_sub_tours = []
                            else:
                                split_sub_tours = b_tour[tr_len + pv_len + mt_len:]
                            return tr, pv, main_tours, split_sub_tours, True
                        elif n == len(b_tour):
                            # print("end3 is {end} n is {nn}".format(end = len(b_tour), nn = n))
                            return tr, pv, main_tours, split_sub_tours, False

    def connectors(self, main_routes, sub_routes):
        connectors = []
        for route_i in main_routes:
            for cus_i in route_i:
                for route_j in sub_routes:
                    for cus_j in route_j:
                        if cus_i == cus_j:
                            connectors.append(cus_i)
        return connectors

    # using cheapest insertion
    def move(self, temp_r, temp_s, node):
        temp_r.remove(node)
        cr = self.cheapest_insertion(temp_r)
        temp_s.append(node)
        cs = self.cheapest_insertion(temp_s)
        return cr, cs 

    
        
if __name__ == "__main__":
    e = Descent()
    # step_two = ([[], [26, 31, 'a']], [], [[10, 21, 19, 34, 35, 2, 27, 30, 25, 7, 47, 23, 5, 'a'], [44, 32, 38, 29, 33, 20, 28, 1, 48, 37, 'a', 43, 14], [13, 42, 22, 'a', 4, 9, 17, 3, 41, 39, 12, 24]], [[], [], []], False)
    step_two = ([[], ['a', 17]], [], [[26, 2, 19, 28, 20, 33, 29, 38, 32, 4, 'a'], [9, 44, 14, 43, 'a', 5, 22, 47, 7, 30, 21, 31, 10, 37, 48], [12, 39, 41, 3, 'a', 1, 34, 35, 27, 25, 42, 23, 13, 24]], [[], [], []], False)
    a = [47, 25, 30, 27, 2, 35, 34, 19, 38, 44, 17, 'a', 26]
    b = [7, 22, 42, 23, 'a', 43, 14, 32, 9, 29, 33, 1, 21]
    c = [13, 'a', 31, 10, 28, 20, 37, 48, 4, 3, 41, 39, 12, 24]
    d = ['a', 5]
    # print(d.opd())
    # print(d.test())   
    # print(d.tpd(step_two[0], step_two[1], step_two[2], step_two[3]))
    print(e.tour_demand(a))
    print(e.tour_length(a) + e.tour_length(b) + e.tour_length(c) + e.tour_length(d))  