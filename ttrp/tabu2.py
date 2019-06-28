#!/usr/bin/env python
# coding=utf-8

from descent import Descent
import random

class Tabu(Descent):
    # def __init__(self):
    #     self.primer = Descent().improvement()

    # return a list stored all root nodes
    def connectors(self, ):
        pass

    # get the root node k of input route
    def get_root(self, ):
        pass

    # get a route's index
    def route_inx(self, ):
        pass

    # compute all routes' length
    def solution_length(self, solution):
        length = 0.0
        for route in solution:
            length += self.tour_length(route)
        return length
    
    # one-point tabu search improvement
    # non-sub-tours part
    def opt1(self, tr, pv, main_tours, split_sub_tours, factor, pi):
        tr_len = len(tr)
        pv_len = len(pv)
        mt_len = len(main_tours)
        sst_len = len(split_sub_tours)
        a_tour = tr + pv + main_tours
        b_tour = tr + pv + main_tours + split_sub_tours

        n = 0
        for route_r in a_tour:
            n += 1
            r_obj = self.tour_length(route_r) # for comparation
            tabu_list = []
            for cus in route_r:
                neighbors = self.opt_neighbors(cus, route_r, tr, pv, main_tours)
                penalty_r = max((self.penalty(route_r, tr, pv, main_tours, split_sub_tours) -
                                 self.one.get_demands()[cus]), 0)
                theta_r = self.penalty(route_r, tr, pv, main_tours, split_sub_tours)
                does neighbors[0] meet the tabu restriction
                    if yes: then finish one iteration
                    continue search new neighbors based on new trial solution
                    if not: increase i_factor by 0.01

    
    # sub-tours part
    def opt2(self, ):
        pass
    
    # two-point tabu search improvement
    def tpt(self, ):
        pass

    # get a trial customer's neighborhood by opt
    def opt_neighbors(self, cus, route_r, tr, pv, main_tours, split_sub_tours):
        b_tour = tr + pv + main_tours + split_sub_tours
        neighborhood = []
        if cus in self.connectors(main_tours, split_sub_tours) or cus == 'a':
            continue
        for route_s in b_tour:
            if route_s == route_r or (self.one.get_types()[cus] == 1 & (route_s in pv or route_s in main_tours)):
                continue
            temp_r = deepcopy(route_r)
            temp_s = deepcopy(route_s)
            move = self.move(temp_r, temp_s, cus)
            neighborhood.append(move)
        return neighborhood # ranked from best to worst

    # get a trial customer's neighborhood by tpt
    def tpt_neighbors(self, cus_i, route_r, tr, pv, main_tours, split_sub_tours):
        b_tour = tr + pv + main_tours + split_sub_tours
        neighborhood = []
        

    # searching part
    # set K as 10/20/30/40/50, K is the search times
    def searching(self):
        primer = Descent().improvement()
        print("PRIMER:", primer)
        tr = primer[0]
        pv = primer[1]
        main_tours = primer[2]
        split_sub_tours = primer[3]
        print(tr, pv, main_tours, split_sub_tours)

        # apply the intensification stage to solution
        # and check INS 💔 I DO NOT KNOW HOW TO APPLY THIS INS
        count = 0
        solution = primer
        best_obj = self.solution_length(primer)
        best_solution_ever = primer
        pi = random.choice([5, 6, 7, 8, 9, 10]) # pi is the searching times
        is_moving = True

        for count in range(K): # or range(pi)?
            neighborhoods = self.get_neighborhood()



    def run(self):
        count = 0
        while count < 10:
            self.searching()
            count += 1
            return 
        while count < 20:
            self.searching()
            count += 1
            return 
        while count < 30:
            self.searching()
            count += 1
            return 
        while count < 40:
            self.searching()
            count += 1
            return 
        while count < 50:
            self.searching()
            count += 1
            return 


if __name__ == "__main__":
    t = Tabu()
    print(t.searching())
