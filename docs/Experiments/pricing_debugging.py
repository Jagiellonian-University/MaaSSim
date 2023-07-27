
import os, sys # add MaaSSim to path (not needed if MaaSSim is already in path)
module_path = os.path.abspath(os.path.join('../..'))
if module_path not in sys.path:
    sys.path.append(module_path)
    
from MaaSSim.utils import get_config, load_G, prep_supply_and_demand, generate_demand, generate_vehicles, initialize_df  # simulator
from MaaSSim.data_structures import structures as inData
from MaaSSim.simulators import simulate
from MaaSSim.visualizations import plot_veh
from MaaSSim.shared import prep_shared_rides
import logging
import matplotlib.pyplot as plt

import pandas as pd
import ExMAS


# Delft

params = get_config('D:/Development/MaaSSim/data/config/delft.json')  # load configuration

params.times.pickup_patience = 3600 # 1 hour of simulation
params.simTime = 4 # 6 minutes hour of simulation
params.nP = 100 # reuqests (and passengers)
params.nV = 50 # vehicles

params.t0 = pd.Timestamp.now()
params.shareability.avg_speed = params.speeds.ride
params.shareability.shared_discount = 0.25
params.shareability.delay_value = 1
params.shareability.WtS = 1.3
params.shareability.price = 1.5 #eur/km
params.shareability.VoT = 0.0035 #eur/s
params.shareability.matching_obj = 'u_veh' #minimize VHT for vehicles
params.shareability.pax_delay = 0
params.shareability.horizon = 600
params.shareability.max_degree = 4
params.shareability.nP = params.nP
params.shareability.share = 1
params.shareability.without_matching = True
params.shareability.operating_cost = 0.5
params.shareability.comm_rate = 0.2

inData = load_G(inData, params)  # load network graph 

inData = generate_demand(inData, params, avg_speed = False)
inData.vehicles = generate_vehicles(inData,params.nV)
inData.vehicles.platform = inData.vehicles.apply(lambda x: 0, axis = 1)
inData.passengers.platforms = inData.passengers.apply(lambda x: [0], axis = 1)
inData.requests['platform'] = inData.requests.apply(lambda row: inData.passengers.loc[row.name].platforms[0], axis = 1) 
inData.platforms = initialize_df(inData.platforms)
inData.platforms.loc[0]=[1,'Uber',30]
params.shareability.share = 1
params.shareability.without_matching = True






inData = ExMAS.main(inData, params.shareability, plot=False) # create shareability graph (ExMAS) 

print("MaaSSIm Simulation Begins")  

inData = prep_shared_rides(inData, params.shareability) # prepare schedules
# Profit Maximization 

inData.sblts.rides

# Solo ride-hailing
#sharing


# Nearest pickup ride-pooling nearst



responses = []
avg_kpi = []
idle_time = []
# Ranges 
for i in range(1, 4):
    params.kpi = i
    sim = simulate(params = params, inData = inData, logger_level = logging.CRITICAL) # simulate
    sim.res[0].veh_kpi.to_csv('D:/Development/GitHub-ProjectV2.0/MaaSSim/docs/tutorials/Results/Simulation/Driver/Test/veh{}.csv'.format(i))
    sim.res[0].pax_kpi.to_csv('D:/Development/GitHub-ProjectV2.0/MaaSSim/docs/tutorials/Results/Simulation/Driver/Test/pax{}.csv'.format(i))
   # sim.res[0].veh_exp['Vehicles'] = sim.res[0].veh_exp.index
   # sim.res[0].veh_exp['ds'] = f"{i}"
    
    #responses.append(sim.res[0].veh_exp)
    
#vehicles = sim.res[0].veh_exp.loc[sim.res[0].veh_exp["nRIDES"] > 0]
#no_of_veh = len(vehicles)
    
#avg_kpi.append(sim.res[0].all_kpi/no_of_veh)
#idle_time.append(vehicles['IDLE'].sum()/no_of_veh)


print('simulation end')


#sim.res[0].veh_kpi.to_csv('D:/Development/GitHub-ProjectV2.0/MaaSSim/docs/tutorials/Results/Simulation/Servicerate/veh{}.csv')
#sim.res[0].pax_kpi.to_csv('D:/Development/GitHub-ProjectV2.0/MaaSSim/docs/tutorials/Results/Simulation/Servicerate/pax{}.csv')


# Profit Maximization revenue of 
#responses = []
#idle_time = []
#avg_kpi = []

#for i in range(1, 4):
 #    params.kpi = i
  #   sim = simulate(params=params, inData=inData, logger_level=logging.CRITICAL)  # simulate
  #   sim.res[0].veh_kpi.to_csv('D:/Development/GitHub-ProjectV2.0/MaaSSim/docs/tutorials/Results/Simulation/day1/veh{}.csv'.format(i))
  #   sim.res[0].pax_kpi.to_csv('D:/Development/GitHub-ProjectV2.0/MaaSSim/docs/tutorials/Results/Simulation/day1/pax{}.csv'.format(i))
  #   sim.res[0].veh_exp['Vehicles'] = sim.res[0].veh_exp.index
   #  sim.res[0].veh_exp['ds'] = f"{i}"

  #   responses.append(sim.res[0].veh_exp)

#vehicles = sim.res[0].veh_exp.loc[sim.res[0].veh_exp["nRIDES"] > 0]
#no_of_veh = len(vehicles)
    
#print('simulation end')

