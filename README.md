# Data Analysis of MyMovez Project

## Structure of NetLogo code

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








