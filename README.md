# WarlightTools

## Commerce
- simultaion for the [Commerce Game](https://www.warzone.com/MultiPlayer?GameID=20134581)
- key idea is to find out which is the best strategy (building cities vs. units)
- currently there is no interaction with other players

- call ```runSimulation(turn_behavior, turn_count)```
- ```turn_behavior(state)``` is a reference to a method, which describes what the player does in a turn
- ```setting1(state)```, ```setting2(state)``` and ```setting3(state)``` show three examples for an implementation
- ```find_best()``` runs several settings for a different number of turns a returns the best parameters for a specific turn count
- a plot shows the development of income, budget and lands of the player
