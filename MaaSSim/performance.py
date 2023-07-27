################################################################################
# Module: performance.py
# Description: Processes raw simulation results into dataframes with network-wide and sinlge pax/veh KPIs
# Rafal Kucharski @ TU Delft, The Netherlands
################################################################################



from .traveller import travellerEvent
from .driver import driverEvent
import pandas as pd
import matplotlib.pyplot as plt
#from MaaSSim.shared import prep_shared_ride



def kpi_pax(*args,**kwargs):
    # calculate passenger indicators (global and individual)

    sim = kwargs.get('sim', None)
    run_id = kwargs.get('run_id', None)
    simrun = sim.runs[run_id]
    paxindex = sim.inData.passengers.index
    df = simrun['trips'].copy()  # results of previous simulation
    dfs = df.shift(-1)  # to map time periods between events
    dfs.columns = [_ + "_s" for _ in df.columns]  # columns with _s are shifted
    df = pd.concat([df, dfs], axis=1)  # now we have time periods
    df = df[df.pax == df.pax_s]  # filter for the same vehicles only
    df = df[~(df.t == df.t_s)]  # filter for positive time periods only
    df['dt'] = df.t_s - df.t  # make time intervals
    ret = df.groupby(['pax', 'event_s'])['dt'].sum().unstack()  # aggreagted by vehicle and event

    ret.columns.name = None
    ret = ret.reindex(paxindex)  # update for vehicles with no record

    ret.index.name = 'pax'
    ret = ret.fillna(0)

    for status in travellerEvent:
        if status.name not in ret.columns:
            ret[status.name] = 0  # cover all statuses

    # meaningful names
    ret['TRAVEL'] = ret['ARRIVES_AT_DROPOFF']  # time with traveller (paid time)
    ret['WAIT'] = ret['RECEIVES_OFFER'] + ret[
        'MEETS_DRIVER_AT_PICKUP']  # time waiting for traveller (by default zero)
    ret['OPERATIONS'] = ret['ACCEPTS_OFFER'] + ret['DEPARTS_FROM_PICKUP'] + ret['SETS_OFF_FOR_DEST']

    kpi = ret.agg(['sum', 'mean', 'std'])
    kpi['nP'] = ret.shape[0]
    return {'pax_exp': ret, 'pax_kpi': kpi}


def kpi_veh(*args, **kwargs):
    """
    calculate vehicle KPIs (global and individual)
    it bases of duration of each event.
    The time per each event denotes the time spent by vehicle BEFORE that event took place.
    From this we can interpret duration of each segments.
    :param args:
    :param kwargs:
    :return: dictionary with kpi per vehicle and system-wide
    """
    
    sim =  kwargs.get('sim', None)
    run_id = kwargs.get('run_id', None)
    simrun = sim.runs[run_id]
    vehindex = sim.inData.vehicles.index
    df = simrun['rides'].copy()  # results of previous simulation
    DECIDES_NOT_TO_DRIVE = df[df.event == driverEvent.DECIDES_NOT_TO_DRIVE.name].veh  # track drivers out
    dfs = df.shift(-1)  # to map time periods between events
    dfs.columns = [_ + "_s" for _ in df.columns]  # columns with _s are shifted
    df = pd.concat([df, dfs], axis=1)  # now we have time periods
    df = df[df.veh == df.veh_s]  # filter for the same vehicles only
    df = df[~(df.t == df.t_s)]  # filter for positive time periods only
    df['dt'] = df.t_s - df.t  # make time intervals
    ret = df.groupby(['veh', 'event_s'])['dt'].sum().unstack()  # aggreagted by vehicle and event
    ret.columns.name = None
    ret = ret.reindex(vehindex)  # update for vehicles with no record
    ret['nRIDES'] = df[df.event == driverEvent.ARRIVES_AT_DROPOFF.name].groupby(
        ['veh']).size().reindex(ret.index)
    ret['nREJECTED'] = df[df.event == driverEvent.IS_REJECTED_BY_TRAVELLER.name].groupby(
        ['veh']).size().reindex(ret.index)
    for status in driverEvent:
        if status.name not in ret.columns:
            ret[status.name] = 0  # cover all statuss

    DECIDES_NOT_TO_DRIVE.index = DECIDES_NOT_TO_DRIVE.values
    ret['OUT'] = DECIDES_NOT_TO_DRIVE
    ret['OUT'] = ~ret['OUT'].isnull()
    ret = ret[['nRIDES', 'nREJECTED', 'OUT'] + [_.name for _ in driverEvent]].fillna(0)  # nans become 0
    
    rides = sim.inData.sblts.rides

    # meaningful names
    ret['TRAVEL'] = ret['ARRIVES_AT_DROPOFF']  # time with traveller (paid time)
    ret['WAIT'] = ret['MEETS_TRAVELLER_AT_PICKUP']  # time waiting for traveller (by default zero)
    ret['CRUISE'] = ret['ARRIVES_AT_PICKUP'] + ret['REPOSITIONED']  # time to arrive for traveller
   
    ret['OPERATIONS'] = ret['ACCEPTS_REQUEST'] + ret['DEPARTS_FROM_PICKUP'] + ret['IS_ACCEPTED_BY_TRAVELLER']
    ret['IDLE'] = ret['ENDS_SHIFT'] - ret['OPENS_APP'] - ret['OPERATIONS'] - ret['CRUISE'] - ret['WAIT'] - ret['TRAVEL']

    ret['PAX_KM'] = ret.apply(lambda x: sim.inData.requests.loc[sim.runs[0].trips[
    sim.runs[0].trips.veh_id == x.name].pax.unique()].dist.sum() / 1000, axis=1)
    
    ret['TTRAV'] = ret.index.map(lambda veh: rides.loc[veh, 'ttrav'])
    ret.index.name = 'veh'
    
        
    ret['DIST'] = ret.index.map(lambda veh: rides.loc[veh, 'dist'])
    ret.index.name = 'veh'
    
    # we need to analyze this code for logic
    #ret['REVENUE'] = ret.apply(lambda x: sim.inData.platforms.loc[sim.inData.vehicles.loc[
     #   x.name].platform].fare, axis=1)
   # ret['REVENUE'] = ret['REVENUE'] * ret['PAX_KM']
   # ret.index.name = 'veh'
    
   # ret['ttrav'] = ret.apply(lambda x: sim.inData.platforms.loc[sim.inData.vehicles.loc[
     #   x.name].platform].fare, axis=1)
    # synatx wrong hay value data frame se uthany ki try krty hyn lakin datafarame ais code mein mention nai ausi k liye sahred.py import krwa raha tha 
    
 
    
    # Driving Time (# time to arrive for traveller)
    ret['DRIVING_TIME'] = ret['ARRIVES_AT_PICKUP'] + ret['ARRIVES_AT_DROPOFF']  # time to arrive for traveller
    ret.index.name = 'veh'
        
    # Driving Distance
    ret['DRIVING_DIST'] = ret['DRIVING_TIME'] * (sim.params.speeds.ride/1000)
    ret.index.name = 'veh'
    
    #ret['pickup_dist'] = ret.apply(lambda row: sim.inData.skim[veh.veh.pos][row.nodes[1]], axis=1)
    
    #still_available_rides['trav_dist'] = still_available_rides['dist'] + still_available_rides[
              #  'pickup_dist']  # distance from driver's initial position to the drop off point of the last passenger
    
   
     #ret['COMMISSION'] = ret.apply(lambda row: sim.inData.sblts.rides[row.name].rdf.commission.sum(), axis=1)
    # please check this syntax we are guving wrong syntax  ret.apply(lambda x: sim.inData.platforms.loc[sim.inData.vehicles.loc[
     #   x.name].platform].fare, axis=1)
    
    ret['FARE'] = ret.index.map(lambda veh: rides.loc[veh, 'fare'])
    ret.index.name = 'veh'
    
    ret['COMMISSION'] = ret.index.map(lambda veh: rides.loc[veh, 'commission'])
    ret.index.name = 'veh'
    
    ret['REVENUE'] = ret.index.map(lambda veh: rides.loc[veh, 'driver_revenue'])
    ret.index.name = 'veh'
    
    # pickup distance
    ret['PICKUP_DIST'] = ret['ARRIVES_AT_PICKUP'] * (sim.params.speeds.ride/1000)  # in km  # distance from driver initial position to the first pickup point
    ret.index.name = 'veh'
    
    ret['TRAVEL_DIST'] = ret['DIST'] + ret['PICKUP_DIST'] # distance from driver's initial position to the drop off point of the last passenger
    ret.index.name = 'veh'
    
    ret['OPERATING_COST'] = ret['TRAVEL_DIST']*(0.0005*100)
    ret.index.name = 'veh'
    
    
    ret['PROFIT'] = ret['REVENUE']- ret['OPERATING_COST']
    ret.index.name = 'veh'
    
   

  

    
   
    
 
   ############################################### 
    ##### This remaining 
  
   
   ####### Profit is remaining
   # ret['profit'
############################################################
    
  #  veh.rdf = pd.concat([veh.rdf, ride])

  #  vehicle_to_trav_dist = veh.rdf.set_index('vehicle')['dist_trav'].to_dict()

# Assuming ret is the DataFrame where you want to add the Trav_DIST column
    #ret = pd.DataFrame(...)  # Replace ... with how you create the ret DataFrame

# Add the Trav_DIST column to the ret DataFrame
   # ret['Trav_DIST'] = ret['vehicle'].map(vehicle_to_trav_dist)

# Set the index name to 'veh'
   # ret.index.name = 'veh'
    
   # ret['PICKUP_DIST'] =ret.apply(lambda row: sim.inData.skim[veh.veh.pos][row.nodes[1]], axis=1)
   # ret['PICKUP_DIST'] = ret['PICKUP_DIST']
   # ret.index.name = 'veh'
    
  #  ret['ttrav'] = ret['ttrav'] 
   # ret.index.name = 'veh'
    
   # ret['commission']= ret['commission']
   # ret.index.name= 'veh'
    #rides = sim.inData.sblts.rides
    #pd.DataFrame(sim.vehs[i].myrides)['paxes'].to_list()
    #ret['REVENUE'] = ret.apply(lambda row: sim.inData.sblts.rides[row.values]['driver_revenue'].to_list(), axis=1)
    
    #ret['REVENUE'] = ret.apply(lambda row: sim.inData.sblts.rides[row.name].rdf.driver_revenue.sum(), axis=1)
    
   # ret['REVENUE'] = ret.apply(lambda row: sim.vehs[row.name].rdf.driver_revenue.sum(), axis=1)
     #_inData.sblts.rides['driver_revenue'] = _inData.sblts.rides['fare'] - _inData.sblts.rides['commission']
    
    #ret['COMMISSION'] = ret.apply(lambda x: sim.inData.platforms.loc[sim.inData.vehicles.loc[
        #x.name].platform].fare, axis=1)
    
    # print karwa lo 
    
    # now lets try to shift the each kpi from shared.py to this file. beacuse this will give us output in csv so we need values of commisiion, revenue and ...
#     ret.apply(lambda x: print(sim.inData.platforms.loc[sim.inData.vehicles.loc[x.name].platform]))
#     print(sim.inData.platforms.loc[sim.inData.vehicles.loc['name'].platform])
    
    #ret = ret[['REVENUE', 'COMMISSION'] + [_.name for _ in driverEvent]]


    kpi = ret.agg(['sum', 'mean', 'std'])
    kpi['nV'] = ret.shape[0]
    return {'veh_exp': ret, 'veh_kpi': kpi}
