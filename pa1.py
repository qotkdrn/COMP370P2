# Name: pa1.py
# Author(s): Liam Sefton, Alex Bae
# Date: 09/23/2022
# Description: Program to read in DFAs and evaluate strings on the given DFAs.
import sys

class DFA:
	""" Simulates a DFA """

	def __init__(self, filename):
		"""
		Initializes DFA from the file whose name is
		filename
		"""
		f = open(filename, 'r')
		self.num_states = f.readline()  #first line of txt file, number of states
		self.alphabet = [ch for ch in f.readline()] #2nd line of txt file, symbols in alphabet
		self.transitions = {} #empty dictionary for transitions
		
		curr_transition = f.readline().strip("\n\t \r")   #first line of transitions
		while "\'" in curr_transition: #while there is a quotation mark in line we are doing transitions
			curr_transition = curr_transition.split(" ")  #convert txt line into list
			curr_state = curr_transition[0]  #current state is line[0]
			if curr_state not in self.transitions.keys():  #create new dictionary for each new key
				self.transitions[curr_state] = {}  
			self.transitions[curr_state][curr_transition[1].strip("\'")] = curr_transition[2]
			curr_transition = f.readline().strip("\n\t \r")

		self.start_state = curr_transition  #initial state is start state, 2nd to last line
		self.accept_states = f.readline().split(" ")  #last line contains accept states
		f.close()

	def simulate(self, str):
		""" 
		Simulates the DFA on input str.  Returns
		True if str is in the language of the DFA,
		and False if not.
		"""
		curr_state = self.start_state
		for ch in str:
			curr_state = self.transitions[curr_state][ch]   #update transitions, current state and ch as key
			                                                #output state as values
		return curr_state in self.accept_states 