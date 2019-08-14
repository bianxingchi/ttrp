#!/usr/bin/env python
# coding=utf-8

class ReadData:
    def __init__(self, filename):
        # self.filename = filename
        
    # def read_txt(self):
        # data_name = "../data/" + self.filename
        data_name = "../data/" + filename
        with open(data_name, "r") as f:
            self.fs = f.readlines()
            line1 = self.fs[0].split()
            line2 = self.fs[1].split()
            self.truck_cap = float(line1[0])
            self.trailer_cap = float(line1[1])
            self.customer_num = int(line1[2])
            self.depot_loc = list(line2[1:3])
        
    def get_locations(self):
        locations = []
        n = 0
        for i in range(2, len(self.fs)):
            linei = self.fs[i].split()
            location = list(linei[1:3])
            locations.append([n, location])
            n += 1
        return locations
        
    def get_demands(self):
        demands = []
        for i in range(2, len(self.fs)):
            linei = self.fs[i].split()
            demand = float(linei[3])
            demands.append(demand)
        return demands

    def get_types(self):
        choices = []
        for i in range(2, len(self.fs)):
            linei = self.fs[i].split()
            choice = int(linei[4])
            choices.append(choice)
        return choices
        

if __name__ == "__main__":
    a = ReadData("TTRP_02.txt")
    print(a.get_demands(), '\n')
    print(a.get_types(), '\n')
    print(a.get_locations(), '\n')
    print(float(a.fs[3].split()[3]))
    print(len(a.fs))

