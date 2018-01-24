# Data Analysis of Obesity Project

This code contains the main functions and notebooks to generate a network and apply interventions in order to predict future states for a group of participants in an obesity project. The code is a replica of the netlogo code provided by [1] with adjustments and calibrations. 

The main concern of this project is to understand, simulate and apply interventions in a social network in order to improve the lifestyle of a population of friends/colleagues/family.


## The ABM: how are the values calculated?

The agents in this ABM contain information about their demographics, about their physical activities and about their food consumption. It is also known how the agents are connected based on information provided by a nomination survey where the participants declare who influences them the most in many aspects.

### Energy Intake

### Energy Expenditure

### Interventions: PA and EI



## Structure of NetLogo code

The original code provided by [1] executes the following steps:

```
|- <func> setup
	|-- <func> setup-world
		|-- set global variables
	|-- <func> setup-agents
		|-- initiate persons attributes
			|-- EI = PA*(0.083*BW*0.85)/0.9
			|-- heigh in meters
			|-- PA is physical activity in [1.4, 4.7]
			|-- Env is the environment = ((random-float (env-max - env-min)) + env-min)
				|-- env-min and env-max are given
			|-- gender, age
			|-- is target? variable
		|-- <func> initiate network
			|-- Makes everyone connected
				|-- <func> which-to-connect
				|-- <func> same-BMI-category
	|-- go "none" #-years-initial
		|-- set variables EI, EE, PA, BW and color
		|-- set time to start
		|-- <loop> Simulate for 365 * number_of_years
			|-- <func> plot-results 'none'
			|-- for each agent
				|-- <func> diffuse-behavior
				|-- <func> update
		|-- <func> baseline-record

|- <func> intervention
	|-- set number of target agents
	|-- get nodes for interventions
		|-- random nodes
		|-- x% most influencial based on centrality degree
		|-- influencial nodes (run the intervention per node and calculate the one who is more beneficial)
			|-- <func> infl-max-nodes
		|-- vulnerable communities
		|-- high risk individuals (BMI >=25)
		|-- highest betweeness
		|-- highest closeness
		|-- highest eigen-vector
		|-- girvan-newman network
	|-- <loop> for each intervention
		|-- <function> apply-intervention
			|-- basically adjust the PA (+17%) or EI (-15%) for the target nodes
		|-- go intervention 	#-years
			|-- <loop> for the time steps
				|-- for each agent
					|-- <func> diffuse-behavior
					|-- <func> update
			|-- reset population for next intervention

```

The BW is altered according to the difference between EI and EE.


## Structure of this code

This code contains a set of files that should work together to run the simulations. 

## Simulation

Each intervention that generates random nodes is run 100 times to garantee that the results are stable.

### Work to do

* zBMI should be used to define the percentage of the population in obesity.

# References 

[1] Beheshti, Rahmatollah, Mehdi Jalalpour, and Thomas A. Glass. "Comparing methods of targeting obesity interventions in populations: An agent-based simulation." SSM-Population Health 3 (2017): 211-218.

[2] Giabbanelli, Philippe J., et al. "Modeling the influence of social networks and environment on energy balance and obesity." Journal of Computational Science 3.1 (2012): 17-27.




