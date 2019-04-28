#!/usr/bin/env python
# coding=utf-8

from descent import Descent
import A B C D # 这里考虑到要不要写一个 base 代码

class Tabu:
    def __init__(self):
        self.primer = Descent.improvement()
    # one-point tabu search mprovement
    def opt1(self, tr, pv, main_tours, split_sub_tours):
        tr_len = len(tr)
        pv_len = len(pv)
        mt_len = len(main_tours)
        sst_len = len(split_sub_tours)
        a_tour = tr + pv + main_tours
        b_tour = tr + pv + main_tours + split_sub_tours
        # print("b_tour of opd1:", b_tour)
        n = 0
        for route_r in a_tour:
            n += 1
            # print("R:", route_r)
            r_obj = self.tour_length(route_r)
            best_obj = deepcopy(r_obj)
            pi = random.choice([5, 6, 7, 8, 9, 10])
            tabu_list = []

            for cus in route_r:
                cj = None
                # print("I:", cus)
                if cus in self.connectors(main_tours, split_sub_tours) or cus == 'a':
                    continue
                penalty_r = max((self.penalty(route_r, tr, pv, main_tours, split_sub_tours) -
                                 self.one.get_demands()[cus]), 0)
                theta_r = self.penalty(route_r, tr, pv, main_tours, split_sub_tours)
                for route_s in b_tour:
                    # print("S:", route_s)
                    if route_s == route_r or (self.one.get_types()[cus] == 1 & (route_s in pv or route_s in main_tours)):
                        continue
                    penalty_s = max((self.tour_demand(route_s) +
                                     self.one.get_demands()[cus] -
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                    theta_s = self.penalty(route_s, tr, pv, main_tours, split_sub_tours)
                    if (route_s in split_sub_tours) & (penalty_s > 0):
                    # if (route_s in split_sub_tours) & (theta_s > 0):
                        continue
                    temp_r = deepcopy(route_r)
                    temp_s = deepcopy(route_s)
                    move = self.move(temp_r, temp_s, cus)
                    obj = self.tour_length(move[0])
                    // 待定义：best_obj
                    otb = False
                    if obj - best_obj >= i_factor * best_obj:
                        otb = True
                    if (penalty_s <= theta_s) & ((penalty_r < theta_r) or (otb == False)): # then(I'm not sure here)
                        if ((move not in tabu_list) or ((move in tabu_list) & (obj < best_obj))) & (obj < r_obj):
                            tabu_list.append((cus, route_s))
                            best_obj = new tour's length
                            # a valid move is an iteration
                            pi -= 1


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
                            return tr, pv, main_tours, split_sub_tours, True
                        elif n == len(a_tour):
                            # print("end1 is {end} n is {nn}".format(end = len(a_tour), nn = n))
                            return tr, pv, main_tours, split_sub_tours, False

    def opt2(self, tr, pv, main_tours, split_sub_tours):
        pass

    def tpt(self, tr, pv, main_tours, split_sub_tours):
        pass
    
    def root_node(self, tour):
        if tour in (tr or pv or main_tours):
            k = "a"
        else:
            
    def searching(self):
        tr = self.primer[0]
        pv = self.primer[1]
        cv = self.primer[2]
        main_tours, sub_tours = [], []
        for seqs in cv:
            main_tours.append(seqs[0])
            sub_tours.append(seqs[1]) # this will be a list of list of list
        split_sub_tours = []
        for tour in sub_tours:
            split_sub_tours += tour

        i_factor = 0.01
        d_factor = 0.1
        for k == 1, ... , K:
            opt1
            opt2
            tpt
            pi = random[5, 10] for FTB
            check local stopping rule
            pi -= 1
        end K loop