import numpy as np

# rewrite to boost::graph in C++
# https://stackoverflow.com/questions/35029305/boostgraph-c-outperformed-by-networkx-python


######################################################
# define rnn
######################################################
# TODO: make it read from pickle or other tf format
sizeX = 3
sizeY = sizeX   # next character prediction
alphabet = ['c', 'a', 't', 'e', ' ']
sizeAlphabet = len(alphabet)


######################################################
# transform rnn to state space graph
######################################################
class StateNN:
    _h = np.array([])  # all values of hidden state: (number_of_hid_layers X hid_units_in_layer X dim_of_hid_units)
    _y = np.array([])  # all values of output state: (number_of_hid_layers X hid_units_in_layer X dim_of_hid_units)

    def __init__(self, name, h, y):
        self.name = name
        self.sizeH = h
        self.sizeY = y

    def set_state(self, h, y):
        print(self.name)
        self._h, self._y = h, y

    def get_h(self):
        print("{} _h = {}".format(self.name, self._h))

    def get_y(self):
        print(self.name + " _y = " + self._y)


# class GraphNN:
#     def __init__(self, name):
#         self.name = name
#
#     def swim(self):
#         print(self.name + " is swimming.")
#
#     def be_awesome(self):
#         print(self.name + " is being awesome.")


# def main():
#     # Set name of Shark object
#     sammy = StateNN("Sammy")
#     sammy.swim()
#     sammy.be_awesome()


if __name__ == "__main__":
    y = np.array([[3, 2, -1, 0, 1], [7, 0, 0, 0, 1], [-1, 2, 3, 6, 7]])
    h = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]])
    s0 = StateNN("s0", y, h)






######################################################
# check properties for state in a graph
######################################################


######################################################
# check graph and get stats
######################################################


