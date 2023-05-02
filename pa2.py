# Name: pa2.py
# Author(s): Alex Bae, Liam Sefton
# Date: 9/29/22
# Description: For this assignment, we will write a program that converts an NFA
#              into an equivalent DFA.

from csv import QUOTE_NONE
from numpy import inner


class NFA:
	""" Simulates an NFA """

	def __init__(self, nfa_filename):
		"""
		Initializes NFA from the file whose name is
		nfa_filename.  (So you should create an internal representation
		of the nfa.)
		"""
		f = open(nfa_filename, 'r')
		self.num_states = int(f.readline().strip("\n\t \r"))
		self.alphabet = [ch for ch in f.readline().strip("\n\t \r")]
		self.Q = range(1, self.num_states + 1)
		q_temp = self.get_powerset(self.Q)
		q_accum = []
		for set in q_temp:
			if set not in q_accum:
				q_accum.append(tuple(set))
		self.Q_PRIME = q_accum
		self.nfa_transitions = {} #maps state to character to set of states
		
		curr_transition = f.readline().strip("\n\t \r")
		while "\'" in curr_transition:
			curr_transition = curr_transition.split(" ")  #convert txt line into list
			curr_state = curr_transition[0]  #current state is line[0]
			if curr_state not in self.nfa_transitions.keys():  #create new dictionary for each new key
				self.nfa_transitions[curr_state] = {}  
			if curr_transition[1].strip("\'") not in self.nfa_transitions[curr_state].keys():
				self.nfa_transitions[curr_state][curr_transition[1].strip("\'")] = []
			
			self.nfa_transitions[curr_state][curr_transition[1].strip("\'")].append(curr_transition[2])
			curr_transition = f.readline().strip("\n\t \r")

		self.q_naught = [f.readline().strip("\n\t \r")]  #initial state is start state, 2nd to last line
		self.F = f.readline().split(" ")  #last line contains accept states
		f.close()


	def get_E_set_iterative(self, set):
		"""This function performs the operation decribed in the textbook
		for E(R), meaning given a set, it returns the set of states reachable by 0
		or more epsilon transitions from the states in the given set."""
		stack = set.copy()
		all_e_states = []
		visited = []

		#For formatting
		for thing in set:
			if type(thing) == list:
				for thing2 in thing:
					all_e_states.append(int(thing2))
			else:
				all_e_states.append(int(thing))
		for i in range(len(all_e_states)):
			all_e_states[i] = int(all_e_states[i])

		#Stack approach to tree structure exploration (treat epsilon transitions as a tree)
		while len(stack) > 0:
			e_states = []
			for state in stack[-1]:
				if state in self.nfa_transitions.keys():
					if 'e' in self.nfa_transitions[state].keys():
						if len(self.nfa_transitions[state]['e']) > 0:
							for st in self.nfa_transitions[state]['e']:
								e_states.append(st)
			stack = stack[:-1] #pop
			for e_state in e_states:
				if e_state not in stack and e_state not in visited:
					stack.append(e_state) #push
					visited.append(e_state) #used to prevent infinite loops from occurring
				if int(e_state) not in all_e_states:
					all_e_states.append(int(e_state))

		return all_e_states


	def get_powerset(self, elems):
		"""Returns set of all subsets of the given set."""
		yield []
		for i in range(len(elems)):
			for x in self.get_powerset(elems[i+1:]): 
				yield [elems[i]] + x 
				
	
	def remove_items(self, list, item):
		"""Used to clear the null set from sets 
		before attempting to get E(set)."""
		c = list.count(item)
		for i in range(c):
			list.remove(item)
		return list
		

	def toDFA(self, dfa_filename):
		"""
		Converts the "self" NFA into an equivalent DFA
		and writes it to the file whose name is dfa_filename.
		The format of the DFA file must have the same format
		as described in the first programming assignment (pa1).
		This file must be able to be opened and simulated by your
		pa1 program.

		This function should not read in the NFA file again.  It should
		create the DFA from the internal representation of the NFA that you 
		created in __init__.
		"""
		dfa_transitions = {}
		temp_f_prime = []

		
		for R in self.Q_PRIME:
			if R not in dfa_transitions.keys():
					dfa_transitions[R] = {} #Initialize inner dict

			for a in self.alphabet:
				if len(R) == 0:
					dfa_transitions[R][a] = () #Self loop on null
				else:
					future_tuple = [] #set of state reachable by states in r with nfa transitions
					for r in R:	
						if str(r) in self.F: #searching for accept states
							if R not in temp_f_prime:
								temp_f_prime.append(R)

						if str(r) in self.nfa_transitions.keys():
							if a in self.nfa_transitions[str(r)].keys():
								if self.nfa_transitions[str(r)][a] not in future_tuple:
									future_tuple.append(self.nfa_transitions[str(r)][a]) #all states reachable by r and a
							else:
								future_tuple.append(())
						else:
							future_tuple.append(())
					future_tuple = self.remove_items(future_tuple, ()) #remove null states

					if len(future_tuple) > 0: 
						dfa_transitions[R][a] = tuple(self.get_E_set_iterative(future_tuple)) #transition prime uses E(nfa_transitions[r][a])
					else:
						dfa_transitions[R][a] = ()
		
		q_naught_prime = (self.q_naught) #convert to singleton set
		F_PRIME = temp_f_prime
		
		f = open(dfa_filename, "w")
		f.write(str(len(self.Q_PRIME)) + "\n") #Num states
		for ch in self.alphabet:
			f.write(ch) #alphabet
		f.write("\n")

		#Writing transitions to file
		for q_prime in self.Q_PRIME:
			for a in self.alphabet:
				curr_transition = str(self.Q_PRIME.index(q_prime) + 1) 
				curr_transition += ' \'' + str(a) + '\' ' 
				if len(dfa_transitions[q_prime][a]) < 2:
					curr_transition += str(self.Q_PRIME.index(dfa_transitions[q_prime][a]) + 1)
				else:
					if () not in dfa_transitions[q_prime][a]:
						curr_transition += str(self.Q_PRIME.index(tuple(sorted(dfa_transitions[q_prime][a]))) + 1)
				f.write(curr_transition + "\n")

		q_naught_prime = self.get_E_set_iterative(q_naught_prime) #Convert q_naught_prime to be E(q_naught_prime)
		q_naught_prime[0] = int(q_naught_prime[0])

		f.write(str(self.Q_PRIME.index(tuple(sorted(q_naught_prime))) + 1) + "\n") #start state

		accept_states_string = ""
		for f_prime in F_PRIME:
			accept_states_string += str(self.Q_PRIME.index(f_prime) + 1) + " " #accept states
		accept_states_string = accept_states_string[:-1]
		f.write(accept_states_string)
		f.close()
