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
            cap = self.one.truck_cap + self.one.trailer_cap
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

    # a_tour is examined 1st
    def opd1(self, tr, pv, main_tours, split_sub_tours):
        tr_len = len(tr)
        pv_len = len(pv)
        mt_len = len(main_tours)
        sst_len = len(split_sub_tours)
        a_tour = tr + pv + main_tours
        b_tour = tr + pv + main_tours + split_sub_tours
        print("b_tour of opd1:", b_tour)
        
        for route_r in a_tour:
            for cus in route_r:
                if cus in self.connectors() or cus == 'a':
                    continue
                penalty_r = max((self.penalty(route_r, tr, pv, main_tours, split_sub_tours) -
                                 self.one.get_demands()[cus]), 0)
                for route_s in b_tour:
                    if route_s == route_r or (self.one.get_types()[cus] == 1 & (route_s in pv or route_s in main_tours)):
                        continue
                    penalty_s = max((self.tour_demand(route_s) +
                                     self.one.get_demands()[cus] -
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                    if (route_s in split_sub_tours) & (penalty_s > 0):
                        continue

                    temp_r = deepcopy(route_r)
                    temp_s = deepcopy(route_s)
                    move = self.move(temp_r, temp_s, cus)
                    cost_of_move = self.tour_length(move[0]) - self.tour_length(route_r)
                    penalty_new_s = max((self.tour_demand(move[1]) +
                                     self.one.get_demands()[cus] - 
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                    temp_r_penalty = max((self.tour_demand(move[0]) - self.tour_cap(route_r, tr, pv, main_tours, split_sub_tours)), 0)
                    penalty_new_r = max((temp_r_penalty - self.one.get_demands()[cus]), 0)
                    if (penalty_new_s <= penalty_s) & ((penalty_new_r < penalty_r) or (cost_of_move < 0)):
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
                        return tr, pv, main_tours, split_sub_tours

    # sub tours is examined then
    def opd2(self, tr, pv, main_tours, split_sub_tours):
        b_tour = tr + pv + main_tours + split_sub_tours
        print("b_tour of opd2:", b_tour)
        tr_len = len(tr)
        pv_len = len(pv)
        mt_len = len(main_tours)
        sst_len = len(split_sub_tours)
        for route_r in split_sub_tours:
            for cus in route_r:
                if cus in self.connectors() or cus == 'a':
                    continue
                penalty_r = max((self.penalty(route_r, tr, pv, main_tours, split_sub_tours) -
                                 self.one.get_demands()[cus]), 0)
                for route_s in b_tour:
                    if route_s == route_r or (self.one.get_types()[cus] == 1 & (route_s in pv or route_s in main_tours)):
                        continue
                    penalty_s = max((self.tour_demand(route_s) +
                                     self.one.get_demands()[cus] - 
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                    if (route_s in split_sub_tours) & (penalty_s > 0):
                        continue

                    temp_r = deepcopy(route_r)
                    temp_s = deepcopy(route_s)
                    move = self.move(temp_r, temp_s, cus)
                    cost_of_move = self.tour_length(move[0]) - self.tour_length(route_r)
                    penalty_new_s = max((self.tour_demand(move[1]) +
                                     self.one.get_demands()[cus] - 
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                    temp_r_penalty = max((self.tour_demand(move[0]) - self.tour_cap(route_r, tr, pv, main_tours, split_sub_tours)), 0)
                    penalty_new_r = max((temp_r_penalty - self.one.get_demands()[cus]), 0)
                    if (penalty_new_s <= penalty_s) & ((penalty_new_r < penalty_r) or (cost_of_move < 0)):
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
                        
                        return tr, pv, main_tours, split_sub_tours
    
    def tpd(self, tr, pv, main_tours, split_sub_tours):
        b_tour = tr + pv + main_tours + split_sub_tours
        print("b_tour of tpd:", b_tour)
        tr_len = len(tr)
        pv_len = len(pv)
        mt_len = len(main_tours)
        sst_len = len(split_sub_tours)

        for route_r in b_tour:
            for cusi in route_r:
                if cusi in self.connectors() or cusi == 'a':
                    continue
                for route_s in b_tour:
                    if route_s == route_r:
                        continue
                    elif (self.one.get_types()[cusi] == 1) & (route_s in (pv or main_tours)):
                        continue
                    for cusj in route_s:
                        if cusj in self.connectors() or cusj == 'a':
                            continue
                        elif (self.one.get_types()[cusj] == 1) & (route_s in (pv or main_tours)):
                            continue
                        penalty_r = max((self.tour_demand(route_r) +
                                     self.one.get_demands()[cusj] - 
                                     self.one.get_demands()[cusi] - 
                                     self.tour_cap(route_r, tr, pv, main_tours, split_sub_tours)), 0)
                        penalty_s = max((self.tour_demand(route_s) +
                                     self.one.get_demands()[cusi] - 
                                     self.one.get_demands()[cusj] - 
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                        if ((route_s in split_sub_tours) & (penalty_s > 0)) or ((route_r in split_sub_tours) & (penalty_r > 0)):
                            continue
                        
                        temp_r = deepcopy(route_r)
                        temp_s = deepcopy(route_s)
                        move1 = self.move(temp_r, temp_s, cusi)
                        move2 = self.move(temp_s, temp_r, cusj)
                        cost_of_exchange = self.tour_length(move1[0]) - self.tour_length(route_r) + \
                                        self.tour_length(move2[0]) - self.tour_length(route_s)
                        
                        penalty_new_r = max((self.tour_demand(move2[1]) +
                                            self.one.get_demands()[cusj] - 
                                            self.one.get_demands()[cusi] - 
                                            self.tour_cap(route_r, tr, pv, main_tours, split_sub_tours)), 0)
                        penalty_new_s = max((self.tour_demand(move2[0]) +
                                            self.one.get_demands()[cusi] - 
                                            self.one.get_demands()[cusj] - 
                                            self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                        if ((penalty_new_r <= penalty_r) & (penalty_new_s <= penalty_new_s)) & \
                            (((penalty_new_r < penalty_r) or (penalty_new_s < penalty_s)) or cost_of_exchange < 0):
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
                            return tr, pv, main_tours, split_sub_tours

    def remove_root(self, route):
        root = None
        for cus in route:
            if cus in self.connectors():
                root = cus
                route.remove(cus)
        return route, root

    def find_main(self, main_tours, removed_route):
        for route_m in main_tours:
            if removed_route[1] in route_m:
                # new_connector = random.choice(route_m)
                return route_m

    def strr(self, main_tours, split_sub_tours):
        print("sub_tours of strr:", split_sub_tours)
        for route in split_sub_tours:
            print("route:", route)
            length = self.tour_length(route)
            print("pre_length", length)
            removed_route = self.remove_root(route)
            its_main = self.find_main(main_tours, removed_route)
            sub_tour = removed_route[0]
            for node in its_main:
                print("try_node:", node)
                if (node == removed_route[1]) or (node == "a"):
                    break
                for n in range(len(sub_tour)):
                    sub_tour.insert(n, node)
                    new_length = self.tour_length(sub_tour)
                    # print("new_length:", new_length)
                    if new_length < length:
                        return sub_tour
            
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

        step_one = self.opd1(tr, pv, main_tours, split_sub_tours)
        print("after opd1:", step_one, '\n')
        step_two = self.opd2(step_one[0], step_one[1], step_one[2], step_one[3])
        print("after opd2:", step_two, '\n')
        step_three = self.tpd(step_two[0], step_two[1], step_two[2], step_two[3])
        print("after tpd:", step_three, '\n')
        step_four = self.strr(step_three[2], step_three[3])
        print("after strr:", step_four)

if __name__ == "__main__":
    d = Descent()
    print(d.improvement())

            