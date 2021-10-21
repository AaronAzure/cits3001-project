# class for initialize and update probability

GAMES = 1000
# GAMES = 1

# class Probability(object):
#     def __init__(self, v0):
#         self.value = v0
#         self.n = 0

#     def sample(self, value):
#         self.sampleExt(value, 1)

#     def sampleExt(self, value, n):
#         self.value = 1 - (1 - self.value)*(1 - float(value) / float(n))
#         self.n += n
        
#     def sampleExtNeg(self, value, n):
#         self.value *= (1- float(value) / float(n))

#     def estimate(self):
#         return self.value

#     def __repr__(self):
#         #return "%0.2f%% (%i)" % (100.0 * float(self.value), self.n)
#         return "{:.2f}%".format(100.0 * float(self.value))
#         # return "%0.2f%% " % (100.0 * float(self.value))

# class Variable(object):
#     def __init__(self, v0, n0):
#         self.total = v0
#         self.samples = n0

#     def sample(self, value):
#         self.sampleExt(value, 1)

#     def sampleBool(self, value):
#         self.sampleExt(int(value), 1)

#     def sampleExt(self, value, n):
#         self.total += value
#         self.samples += n

#     def estimate(self):
#         if self.samples > 0:
#             return float(self.total) / float(self.samples)
#         else:
#             return 0.0
#     def __repr__(self):
#         if self.samples:
#             #return "%0.2f%% (%i)" % ((100.0 * float(self.total) / float(self.samples)), self.samples)
#             return "%0.2f%% " % ((100.0 * float(self.total) / float(self.samples)))
#         else:
#             return "UNKNOWN"

# supportSuspects = [Variable(0.4, 1.0) for x in range(5)]
# print(supportSuspects)