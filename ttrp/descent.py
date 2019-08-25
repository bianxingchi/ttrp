#!/usr/bin/env python
# coding=utf-8

from readdata import ReadData
from construction import Construction
from copy import deepcopy
import random

class Descent(Construction):
    def tour_demand(self, tour):
        demands = 0.0
        for cus in tour:
            if cus == 'a':
                continue
            demands += self.one.get_demands()[cus]
        return demands
    
    # 这一部分待完善，为了避免再调用导致的返回值不一致，应当统一使用已经储存的值
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

    # using cheapest insertion
    def move(self, temp_r, temp_s, node):
        temp_r.remove(node)
        cr = self.cheapest_insertion(temp_r)
        temp_s.append(node)
        cs = self.cheapest_insertion(temp_s)
        return cr, cs 

    def remove_empty(self, routes):
        for route in routes:
            if route == []:
                routes.remove(route)
        return routes
    
    # a_tour is examined 1st
    def opd1(self, tr, pv, main_tours, split_sub_tours):
        tr_len = len(tr)
        pv_len = len(pv)
        mt_len = len(main_tours)
        sst_len = len(split_sub_tours)
        a_tour = tr + pv + main_tours
        b_tour = tr + pv + main_tours + split_sub_tours
        # print("b_tour of opd1:", b_tour)
        n = 0 # max n is len(a_tour)
        for route_r in a_tour:
            n += 1
            # print("R:", route_r)
            for cus in route_r:
                # print("I:", cus)
                if cus in self.connectors(main_tours, split_sub_tours) or cus == 'a':
                    continue
                penalty_r = max((self.penalty(route_r, tr, pv, main_tours, split_sub_tours) -
                                 self.one.get_demands()[cus]), 0)
                theta_r = self.penalty(route_r, tr, pv, main_tours, split_sub_tours)
                for route_s in b_tour:
                    # print("S:", route_s)
                    if route_s == route_r:
                        continue
                    if (self.one.get_types()[cus] == 1) and ((route_s in pv) or (route_s in main_tours)):
                        # print("→ t.c. customer:", cus)
                        continue
                    penalty_s = max((self.tour_demand(route_s) +
                                     self.one.get_demands()[cus] -
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                    theta_s = self.penalty(route_s, tr, pv, main_tours, split_sub_tours)
                    if (route_s in split_sub_tours) and (penalty_s > 0):
                    # if (route_s in split_sub_tours) and (theta_s > 0):
                        continue
                    temp_r = deepcopy(route_r)
                    temp_s = deepcopy(route_s)
                    move = self.move(temp_r, temp_s, cus)
                    cost_of_move = self.tour_length(move[0]) + self.tour_length(move[1]) - self.tour_length(route_r) - self.tour_length(route_s)
                    if (penalty_s <= theta_s) and ((penalty_r < theta_r) or (cost_of_move < 0)):
                        print("→ S Matched (opd1):", cus, route_s)
                        for n, i in enumerate(b_tour):
                            if i == route_r:
                                b_tour[n] = move[0]
                        for n, i in enumerate(b_tour):
                            if i == route_s:
                                b_tour[n] = move[1]
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
                        # remove empty list from a type of routes
                        tr = self.remove_empty(tr)
                        pv = self.remove_empty(pv)
                        main_tours = self.remove_empty(main_tours)
                        split_sub_tours = self.remove_empty(split_sub_tours)
                        return tr, pv, main_tours, split_sub_tours, True
                    elif n == len(a_tour):
                        # print("end1 is {end} n is {nn}".format(end = len(a_tour), nn = n))
                        return tr, pv, main_tours, split_sub_tours, False

    # sub tours is examined then
    def opd2(self, tr, pv, main_tours, split_sub_tours):
        b_tour = tr + pv + main_tours + split_sub_tours
        # print("b_tour of opd2:", b_tour)
        tr_len = len(tr)
        pv_len = len(pv)
        mt_len = len(main_tours)
        sst_len = len(split_sub_tours)
        n = 0

        # if sub-tours is null, then below
        m = 0
        for r in split_sub_tours:
            if r == []:
                m += 1
        if m == len(split_sub_tours):
            return tr, pv, main_tours, split_sub_tours, False

        for route_r in split_sub_tours:
            # print("sub_r:", route_r)
            n += 1
            if route_r == []:
                continue
            for cus in route_r:
                # print("sub_cus:", cus)
                if cus in self.connectors(main_tours, split_sub_tours):
                    continue
                if cus == 'a':
                    continue
                penalty_r = max((self.penalty(route_r, tr, pv, main_tours, split_sub_tours) -
                                 self.one.get_demands()[cus]), 0)
                theta_r = self.penalty(route_r, tr, pv, main_tours, split_sub_tours)
                for route_s in b_tour:
                    # print("try_subS:", route_s)
                    if route_s == route_r:
                        continue
                    if (self.one.get_types()[cus] == 1) and ((route_s in pv) or (route_s in main_tours)):
                        continue
                    penalty_s = max((self.tour_demand(route_s) +
                                     self.one.get_demands()[cus] - 
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                    theta_s = self.penalty(route_s, tr, pv, main_tours, split_sub_tours)                 
                    # if (route_s in split_sub_tours) and (penalty_s > 0):
                    if (route_s in split_sub_tours) and (penalty_s > 0):
                        continue

                    temp_r = deepcopy(route_r)
                    temp_s = deepcopy(route_s)
                    move = self.move(temp_r, temp_s, cus)
                    # print("opd2 after move:", move)
                    cost_of_move = self.tour_length(move[0]) + self.tour_length(move[1]) - self.tour_length(route_r) - self.tour_length(route_s)
                    if (penalty_s <= theta_s) and ((penalty_r < theta_r) or (cost_of_move < 0)):
                        print("→ S Matched (opd2):", cus, route_s)
                        for n, i in enumerate(b_tour):
                            if i == route_r:
                                b_tour[n] = move[0]
                        for n, i in enumerate(b_tour):
                            if i == route_s:
                                b_tour[n] = move[1]
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
                        # remove empty list from a type of routes
                        # tr = self.remove_empty(tr)
                        # pv = self.remove_empty(pv)
                        # main_tours = self.remove_empty(main_tours)
                        # split_sub_tours = self.remove_empty(split_sub_tours)
                        return tr, pv, main_tours, split_sub_tours, True
                    elif n == len(split_sub_tours):
                        # print("end2 is {end} n is {nn}".format(end = len(split_sub_tours), nn = n))
                        return tr, pv, main_tours, split_sub_tours, False
    
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
                if cusi in self.connectors(main_tours, split_sub_tours):
                    continue
                if cusi == 'a':
                    continue
                for route_s in b_tour:
                    if route_s == route_r:
                        continue
                    if (self.one.get_types()[cusi] == 1) and ((route_s in pv) or (route_s in main_tours)):
                        continue
                    for cusj in route_s:
                        if cusj in self.connectors(main_tours, split_sub_tours) or cusj == 'a':
                            continue
                        if (self.one.get_types()[cusj] == 1) and ((route_r in pv) or (route_r in main_tours)):
                            continue
                        penalty_r = max((self.tour_demand(route_r) +
                                     self.one.get_demands()[cusj] - 
                                     self.one.get_demands()[cusi] - 
                                     self.tour_cap(route_r, tr, pv, main_tours, split_sub_tours)), 0)
                        theta_r = self.penalty(route_r, tr, pv, main_tours, split_sub_tours)
                        penalty_s = max((self.tour_demand(route_s) +
                                     self.one.get_demands()[cusi] - 
                                     self.one.get_demands()[cusj] - 
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                        theta_s = self.penalty(route_s, tr, pv, main_tours, split_sub_tours)
                        if (route_s in split_sub_tours) and (penalty_s > 0):
                            continue
                        if (route_r in split_sub_tours) and (penalty_r > 0):
                            continue

                        temp_r = deepcopy(route_r)
                        temp_s = deepcopy(route_s)
                        # after move1, cusi removed from temp_r and insert into temp_s
                        move1 = self.move(temp_r, temp_s, cusi)
                        # after move2, cusj removed from temp_s (already have cusi)
                        # and insert into temp_r (which is removed cusi)
                        # only use move2's result, bcz it's exchange
                        # move2[0] is temp_s; move2[1] is temp_r
                        move2 = self.move(temp_s, temp_r, cusj)

                        cost_of_exchange = self.tour_length(move2[1]) - self.tour_length(route_r) + self.tour_length(move2[0]) - self.tour_length(route_s)
                        
                        # 这儿看起来有点混乱，但其实逻辑没错
                        # 问题在于这种 and 和 or 的组合，是不是就正确还原了预想的逻辑
                        # ===========================================================
                        if ((penalty_r <= theta_r) and (penalty_s <= theta_s)) and ((penalty_r < theta_r) or (penalty_s < theta_s) or cost_of_exchange < 0):
                            print("→ S Matched (tpd):", cusi, route_s, "|", cusj, route_r)
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
                            # remove empty list from a type of routes
                            tr = self.remove_empty(tr)
                            pv = self.remove_empty(pv)
                            main_tours = self.remove_empty(main_tours)
                            split_sub_tours = self.remove_empty(split_sub_tours)
                            return tr, pv, main_tours, split_sub_tours, True
                        elif n == len(b_tour):
                            # print("end3 is {end} n is {nn}".format(end = len(b_tour), nn = n))
                            return tr, pv, main_tours, split_sub_tours, False

    def remove_root(self, route, main_routes, sub_routes):
        root = None
        temp_r = deepcopy(route)
        for cus in route:
            if cus in self.connectors(main_routes, sub_routes):
                root = cus
                temp_r.remove(cus)
        return temp_r, root

    def find_main(self, main_tours, removed_route):
        for route_m in main_tours:
            if removed_route[1] in route_m:
                # new_connector = random.choice(route_m)
                return route_m
    
    def connectors(self, main_routes, sub_routes):
        connectors = []
        for route_i in main_routes:
            for cus_i in route_i:
                for route_j in sub_routes:
                    for cus_j in route_j:
                        if cus_i == cus_j:
                            connectors.append(cus_i)
        return connectors

    def strr(self, main_tours, split_sub_tours):
        # print("sub_tours of strr:", split_sub_tours)
        n = 0
        for route in split_sub_tours:
            n += 1
            # print("n is:", n)
            if ((len(route) == 2) or (len(route) == 0)) and (n == len(split_sub_tours)): # 可能最后一次在这跳出去了，导致输出是 None
                return split_sub_tours, False
            elif (len(route) == 2) or (len(route) == 0):
                continue
            # print("route:", route)
            length = self.tour_length(route)
            # print("pre_length", length)
            # this returns route and the removed root
            removed_route = self.remove_root(route, main_tours, split_sub_tours)
            its_main = self.find_main(main_tours, removed_route)
            sub_tour = deepcopy(removed_route[0])
            # print("removed route:", sub_tour)
            # print("its main:", its_main)
            # print("sub_tour", sub_tour)
            
            for node in its_main:
                # print("try_node:", node)
                if (node == removed_route[1]) or (node == "a"):
                    continue
                # print("len range:", len(removed_route[0]))
                for n in range(len(sub_tour)):
                    sub_tour.insert(n, node)
                    new_length = self.tour_length(sub_tour)
                    # print("new_length:", new_length)
                    if new_length < length:
                        print("→ Root changed (strr):", node)
                        for n, i in enumerate(split_sub_tours):
                            if i == route:
                                split_sub_tours[n] = sub_tour
                        return split_sub_tours, True
                    elif n == len(split_sub_tours):
                        print("end4 is {end} n is {nn}".format(end = len(split_sub_tours), nn = n))
                        return split_sub_tours, False

    def two_opt(self, route):
        # for route in routes:
        if route == []:
            return route
        best = route
        improved = True
        while improved:
            improved = False
            for i in range(len(route) - 2):
                for j in range(i + 1, len(route)):
                    if j - 1 == 1:
                        continue
                    new_route = route[:i] + list(reversed(route[i:j + 1])) + route[j + 1:]
                    # new_route = route[:]
                    # new_route[i:j] = route[j-1:i-1:-1]
                    if self.tour_length(new_route) < self.tour_length(route):
                        best = new_route
                        improved = True
            route = best
        return best
            
    # descent and tabu
    def improvement(self):
        # variables to guarantee do not call
        # cheapest insertion function secondly
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

        is_moving = True
        while is_moving:
            print("before looping:", tr, pv, main_tours, split_sub_tours)
            step_one = self.opd1(tr, pv, main_tours, split_sub_tours)
            print("after 1:", step_one)
            step_two = self.opd2(step_one[0], step_one[1], step_one[2], step_one[3])
            print("after 2:", step_two)
            step_three = self.tpd(step_two[0], step_two[1], step_two[2], step_two[3])
            print("after 3:", step_three)
            step_four = self.strr(step_three[2], step_three[3])
            print("after 4:", step_four)
            tr, pv, main_tours, split_sub_tours = step_three[0], step_three[1], step_three[2], step_four[0]
            
            # tr, pv, main_tours, split_sub_tours = step_three[0], step_three[1], step_three[2], step_three[3]
            # print("objective:", self.tour_length(tr) + self.tour_length(pv) + self.tour_length(main_tours) + self.tour_length(split_sub_tours), "\n")
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
            print("after  looping:", tr, pv, main_tours, split_sub_tours, objective, penalty, '\n')
            if (step_one[-1] == False) and (step_two[-1] == False) and (step_three[-1] == False) and (step_four[-1] == False):
            # if (step_one[-1] == False) and (step_two[-1] == False):
            # if penalty == 0.0:
                print("→ DESCENT: NO move occured & apply 2-opt")
                new_tr, new_pv, new_mts, new_ssts = [], [], [], []
                if tr == []:
                    pass
                else:
                    for route in tr:
                        new_route = self.two_opt(route)
                        new_tr.append(new_route)
                if pv == []:
                    pass
                else:
                    for route in pv:
                        new_route = self.two_opt(route)
                        new_pv.append(new_route)
                if main_tours == []:
                    pass
                else:
                    for route in main_tours:
                        new_route = self.two_opt(route)
                        new_mts.append(new_route)
                if split_sub_tours == []:
                    pass
                else:
                    for route in split_sub_tours:
                        new_route = self.two_opt(route)
                        new_ssts.append(new_route)
                is_moving = False
        initial_solution = [new_tr, new_pv, new_mts, new_ssts]
        return initial_solution
        
    # descent used within tabu search
    def inner_improve(self, tr, pv, main_tours, split_sub_tours):
        is_moving = True
        while is_moving:
            print("before inner descent:", tr, pv, main_tours, split_sub_tours)
            step_one = self.opd1(tr, pv, main_tours, split_sub_tours)
            print("after 1:", step_one)
            step_two = self.opd2(step_one[0], step_one[1], step_one[2], step_one[3])
            print("after 2:", step_two)
            step_three = self.tpd(step_two[0], step_two[1], step_two[2], step_two[3])
            print("after 3:", step_three)
            step_four = self.strr(step_three[2], step_three[3])
            print("after 4:", step_four)
            tr, pv, main_tours, split_sub_tours = step_three[0], step_three[1], step_three[2], step_four[0]
            # print("objective:", self.tour_length(tr) + self.tour_length(pv) + self.tour_length(main_tours) + self.tour_length(split_sub_tours), "\n")
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
            print("after  looping:", tr, pv, main_tours, split_sub_tours, objective, penalty, '\n')
            if (step_one[-1] == False) and (step_two[-1] == False) and (step_three[-1] == False) and (step_four[-1] == False):
            # if (step_one[-1] == False) and (step_two[-1] == False):
            # if penalty == 0.0:
                print("→ inner-DESCENT: NO move occured & apply 2-opt")
                new_tr, new_pv, new_mts, new_ssts = [], [], [], []
                if tr == []:
                    pass
                else:
                    for route in tr:
                        new_route = self.two_opt(route)
                        new_tr.append(new_route)
                if pv == []:
                    pass
                else:
                    for route in pv:
                        new_route = self.two_opt(route)
                        new_pv.append(new_route)
                if main_tours == []:
                    pass
                else:
                    for route in main_tours:
                        new_route = self.two_opt(route)
                        new_mts.append(new_route)
                if split_sub_tours == []:
                    pass
                else:
                    for route in split_sub_tours:
                        new_route = self.two_opt(route)
                        new_ssts.append(new_route)
                is_moving = False
        improved_solution = [new_tr, new_pv, new_mts, new_ssts]
        return improved_solution   
        
if __name__ == "__main__":
    d = Descent()
    print("initial solution:", d.improvement())

            