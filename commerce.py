#!/usr/bin/python
#-*- coding:utf-8 -*-
import random
import time
import numpy as np
import matplotlib.pyplot as plt

from dataclasses import dataclass
from random import random

#----------------------------------------------------------------------------#
@dataclass
class GameState:
  #--- current state
  turn       = 0
  lands      = np.zeros(3)    # each land has an entry in this list, with the number of cities on it
  income     = int(3)
  budget     = 0
  units      = 0
  weak_count = 6
  #--- development in the turn
  new_units   = 0
  new_cities  = 0
  new_lands   = 0
  #--- game settings
  weak_prob  = 708.0 / 2253.0 #probability of a finding a weak land
  strength_normal  = 80    # number of units in normal neutral territories
  strength_weak    = 25    # number of units in weak neutral territories
  count_weak       = 6     # number of weak territories next to the player
  attack_rate      = 0.6
  defense_rate     = 0.7
  cost_city        = 4
  cost_unit        = 1
  cost_multiplier  = 12    # each 12 units the cost increases by 1

##--------------------------------------------------------------------------##
def buildCity(state, max_count = -1, max_cost = -1):
  build_more  = True    # flag indicating to build more cities
  build_count = 0       # total number of cities build this turn
  total_cost  = 0       # money spend on cities this turn

  while build_more:
    min_idx    = np.argmin(state.lands)           # land with least cities gets the next one
    cost       = state.lands[min_idx] + state.cost_city # next city costs 'number_of_cities + 4'
    build_more = False

    if (cost <= state.budget):                 #if we have enough budget build a city
      state.lands[min_idx] += 1
      state.budget -= cost
      total_cost   += cost
      build_count  += 1
    else:
      break

    if (max_count < 0 and max_cost < 0):
      build_more = True
    elif (max_count >= 0 and max_cost < 0):
      if (build_count < max_count):
        build_more = True
    elif (max_count < 0 and max_cost >= 0):
      if (total_cost < max_cost):
        build_more = True
    elif (max_count >= 0 and max_cost >= 0):
      if (build_count < max_count and total_cost < max_cost):
        build_more = True

  state.new_cities += build_count
  return build_count

##--------------------------------------------------------------------------##
# state      - current state of the player
# max_cost   - maximum gold that we want to spend on units in this turn; -1 if no limit
# min_income - minimum income a player needs, to build units; -1 if no minimum income is necessary
def buyUnit(state, max_cost = -1, min_income = -1):
  build_more  = True  # flag indicating to build more units
  build_count = 0     # total number of units build this turn
  total_cost  = 0     # money spend on units this turn

  if (state.income < min_income):
    return 0

  while build_more:
    cost = int(build_count / state.cost_multiplier) + state.cost_unit;
    #---
    if (state.budget >= cost):
      state.budget -= cost
      state.units  += 1
      build_count  += 1
      total_cost   += cost
    else:
      break
    #---
    if (max_cost >= 0 and total_cost < max_cost):
      build_more = True

  state.new_units += build_count
  return build_count

##--------------------------------------------------------------------------##
def attack(state):
  defending = state.strength_normal
  conquered = 0

  if (state.weak_count > 0):
    defending = state.strength_weak

  destroy = int(round(state.units * state.attack_rate)) # number of enemies our current units can destroy
  lose    = int(round(defending * state.defense_rate))

  if (destroy > defending):     # if we can destroy more units than units exist in one adjacent land, we attack, one army must stand guard
    state.lands = np.append(state.lands, [0])
    state.units -= lose
    if (state.weak_count > 0):
      state.weak_count -= 1
    if (random() < state.weak_prob):
      state.weak_count += 1
      #print("found weak land")

    conquered += 1
    conquered += attack(state)

  state.new_lands += conquered
  return conquered

##--------------------------------------------------------------------------##
def resetState():
  state = GameState()
  state.turn       = 0
  state.lands      = np.zeros(3)    # each land has an entry in this list, with the number of cities on it
  state.income     = int(3)
  state.budget     = 0
  state.units      = 0
  state.new_units  = 0
  state.new_cities = 0
  state.new_lands  = 0
  state.weak_count = 6
  return state

#----------------------------------------------------------------------------#
#try different settings and find the best tactic for the turn count
def find_best():
  turns  = [10, 15, 20, 25, 30, 35, 40, 45, 50]
  output = ([("", [0], [0], [0], [0], [0])])*len(turns)
  best   = [0]*len(turns)

  city_unit_rate = 0.0
  state = GameState()
  for i in range(0, len(turns)):
    sim_turns = turns[i]
    print(sim_turns)

    #--- save the progress over the turns
    dev_income = [0]*sim_turns
    dev_budget = [0]*sim_turns
    dev_units  = [0]*sim_turns
    dev_lands  = [0]*sim_turns
    dev_cities = [0]*sim_turns

    for min_income in range(0, 144, 6):    # minimum income before building units
      for k in range(0, 101, 10):          # cost ratio between cities : units
        city_unit_rate = float(k / 100.0)
        for j in range(1,  11):            # perecentage of lands, that get a new city
            state = resetState()
            city_count = 0
            land_count = len(state.lands)
            for turn in range(0, sim_turns, 1):  # turns
              #--- advance turn
              state.turn   += 1
              state.budget += state.income
              #--- update build settings for this turn
              max_city_count = j*len(state.lands)/10
              max_city_cost  = int(city_unit_rate * state.budget)
              max_unit_cost  = int((1.0 - city_unit_rate) * state.budget)
              #---
              new_cities = buildCity(state, max_city_count, max_city_cost)
              new_units  = buyUnit(state, max_unit_cost , min_income)
              new_lands  = attack(state)
              #---
              state.income += new_cities
              city_count   += new_cities
              land_count   += new_lands

              if new_lands > 0:
                print((turn, new_lands, land_count))
              #---
              dev_income[turn] = state.income
              dev_budget[turn] = state.budget
              dev_units[turn]  = state.units
              dev_lands[turn]  = len(state.lands)
              dev_cities[turn] = city_count

            # check if we found a better solution
            if (best[i] < state.income):
              best[i] = state.income
              message = "turn %d \t" % len(dev_income)
              message += "income %d \tbudget %d \t" % (state.income, state.budget)
              message += "cities %d \t\tunits %d \tlands %d " % (city_count, state.units, len(state.lands))
              message += "\t build_percentage: %f  city_to_unit: %f  min_income: %d " % (float(j / 10.0), city_unit_rate, min_income)
              message += np.array2string(state.lands)
              output[i] = (message, dev_income, dev_budget, dev_units, dev_lands, dev_cities)

  #--- print final best result for all turns
  for o in output:
    print(o[0])
    plt.plot(o[1], label = "income")  #income
    plt.plot(o[2], label = "budget")  #budget
    plt.plot(o[4], label = "lands")  #lands
    plt.legend()
    plt.ylabel('income / budget / territories')
    plt.show()

  return output

#----------------------------------------------------------------------------#
#build as most cities as possible
#THEN IF we build at least 1 city build as most units as possible
#attack
def setting1(state):
  # build as most cities as possible
  new_cities = buildCity(state)
  #if we build at least one city buy as much units as possible
  if (new_cities > 0):
    buyUnit(state)
  #--- attack if possible
  attack(state)

#----------------------------------------------------------------------------#
#build 1 city
#if so buy 12 units, if we have 12 income
#afterwards build more cities and units
def setting2(state):
  min_income = 12                 # minimum income before building units
  # build 1 city
  new_cities = buildCity(state, 1)
  #if we build 1 city buy at most 12 units
  if (new_cities > 0):
    buyUnit(state, min_income, min_income)
    buildCity(state)
    buyUnit(state, -1, min_income)
  #--- attack if possible
  attack(state)

#----------------------------------------------------------------------------#
#build as most cities as possible
#build as most units as possible if the income is > 24
#attack
def setting3(state):
  min_income = 24
  # build as most cities as possible
  buildCity(state)
  buyUnit(state, -1, min_income)
  #--- attack if possible
  attack(state)

#----------------------------------------------------------------------------#
def runSimulation(turn_behavior, turn_count):
  state = resetState()
  output = ([("", [0], [0], [0], [0], [0])])
  #--- save the progress over the turns
  dev_income = [0]*turn_count
  dev_budget = [0]*turn_count
  dev_units  = [0]*turn_count
  dev_lands  = [0]*turn_count
  dev_cities = [0]*turn_count
  #---
  city_count = 0
  land_count = len(state.lands)
  for turn in range(0, turn_count, 1):  # turns
    #--- advance turn
    state.turn   += 1
    state.budget += state.income
    state.new_units  = 0
    state.new_cities = 0
    state.new_lands  = 0

    #--- update build settings for this turn
    turn_behavior(state)
    #--- save progress
    state.income += state.new_cities
    city_count   += state.new_cities
    land_count   += state.new_lands
    #---
    dev_income[turn] = state.income
    dev_budget[turn] = state.budget
    dev_units[turn]  = state.units
    dev_lands[turn]  = len(state.lands)
    dev_cities[turn] = city_count

  #--- save final result
  message = "Result of simulation:\n"
  message += "income %d \tbudget %d \t" % (state.income, state.budget)
  message += "cities %d \t\tunits %d \tlands %d " % (city_count, state.units, len(state.lands))
  message += "city distribution: "
  message += np.array2string(state.lands)
  output = (message, dev_income, dev_budget, dev_units, dev_lands, dev_cities)

  #--- print final result
  print(output[0])
  plt.plot(output[1], label = "income")  #income
  plt.plot(output[2], label = "budget")  #budget
  plt.plot(output[4], label = "lands")  #lands
  plt.legend()
  plt.ylabel('income / budget / territories')
  plt.show()

  return output

#----------------------------------------------------------------------------#
timestamp_start = time.time()
find_best()
turn_count = 50
runSimulation(setting1, turn_count)
runSimulation(setting2, turn_count)
runSimulation(setting3, turn_count)
print("total time: " + str((time.time()-timestamp_start)*1000) + "ms")
