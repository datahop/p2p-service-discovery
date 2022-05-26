import math

class Model:

    def __init__(self):
        self.capacity = 10
        self.table = {}
        self.counter = 0
        self.ad_lifetime = 10

    def get_id_modifier(self, iD, table):
        current_ids = [x['id'] for x in table.values()]
        return math.pow(((current_ids.count(iD))/len(table)), 0.2)
    def get_basetime(self, table):
        return (30*self.ad_lifetime)/math.pow(1-len(table)/self.capacity, 5)


    def add(self, req):
        self.table[self.counter] = req
        self.counter += 1

    def get_waiting_time(self, ID):
        table = self.table
        if(len(table) > 0):
            base_waiting_time = self.get_basetime(table)
            id_modifier = self.get_id_modifier(ID, table)
            return base_waiting_time * id_modifier
        else:
            return 0


m = Model()
print(m.get_waiting_time('id1'))

req = {'id': 'id1'}
m.add(req)
print(m.get_waiting_time('id1'))

req = {'id': 'id2'}
m.add(req)
print(m.get_waiting_time('id1'))