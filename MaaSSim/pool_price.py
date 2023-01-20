################################################################################
# Module: pool_price.py
# Making choices betweenpooled and single rides in MaaSSim
# uses (ExMAS) 
# Rafal Kucharski @ Jagiellonian University
################################################################################

def pool_price_fun(sim, veh, request):
    # function used inside the f_match to update the choice of the driver (pool/single)

    logger = sim.logger.critical # set what do you wantto see from the logger
    
    if len(request.rides)>1: # only if there is a choice
        logger('this is request {} with {} available rides.'.format(request.pax_id, request.rides))
        available_rides = sim.inData.sblts.rides.loc[request.rides] # this is set in shared.py
        still_available_rides = list()
        for ride_index, ride in available_rides.iterrows():
            if all([sim.pax[_].pax.event.value <= 1 for _ in ride.indexes]):
                still_available_rides.append(ride_index) # see all the travellers of this pooled ride are still available
                logger("ride {} available {}".format(ride.name, [sim.pax[_].pax.event.value for _ in ride.indexes])) 
            else:
                logger("ride {} not available {}".format(ride.name, [sim.pax[_].pax.event.value for _ in ride.indexes]))
        logger('this is reuqest {} with {} still available rides.'.format(request.pax_id, still_available_rides))

        if len(still_available_rides)>1: # only if we still have a choice
            
            still_available_rides = sim.inData.sblts.rides.loc[still_available_rides]

            #### HERE COMES YOUR CHOICE FUNCTIONS
            #This is a random function. 
            #my_choice = still_available_rides.sample(1).squeeze() # random choice - to be overwritten with different func
            #==================================================================
            # add cost column to the still_available_rides - trip distance x cost per km (this is fixed)
            # add column profit to the still_available_rides - Revenue - cost
            # driver chooses the ride with maximum profit
            #==================================================================
            still_available_rides["this_driver_revenue"] = still_available_rides["driver_revenue"] + dist[veh,ride_origin] # add distances to all the trip origins
            # RK: TODO add fuel costs

            #RK TODO: Compute costs: TIME + DISTANCE + FUEL + penalty for pooled rides

            my_choice = still_available_rides[still_available_rides["this_driver_revenue"]==still_available_rides["this_driver_revenue"].max()].squeeze() # RK: Add the cost to arrive at origin (distance)
            # print(my_choice)

            # MAKE TWO OPTIONS OF CHOICE: DETERMINISTIC AND PROBSBILISTIC:
            # P(R)= exp(beta * Profit_R)/ sum_all the rides( exp(beta * Profit_R)

            logger('vehicle {} has chosen to serve request {} with a ride {} of degree {}, with travellers {}.'.format(veh.id, request.pax_id, my_choice.name, my_choice.degree, my_choice.indexes ))

            # set the schedule of this request - to be used in simulations
            for pax in my_choice.indexes:
                sim.inData.requests.loc[pax].sim_schedule = my_choice.sim_schedule
                # maybe here we need to update the position and leader of the schedule - and set that the schedule got triggered? - so far no bugs
    
    return request, sim

    


            
                
     
        
       

        

            







