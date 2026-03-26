def plantstate(planttemp,temptarget, planthum, humtarget, plantmoist,moisttarget):


    #Defining plant tolerance to avoid too strict analysis
    TEMP_TOLERANCE = 6 
    HUM_TOLERANCE = 15
    MOIST_TOLERANCE = 10

#Defining plant state  :
# 
# -1 is not enough
# 0 is perfect
# 1 is too much
    temp_state = 0
    hum_state = 0
    moist_state = 0


    if planttemp + TEMP_TOLERANCE  < temptarget:
        temp_state = -1
    elif planttemp - TEMP_TOLERANCE  > temptarget:
        temp_state = 1

    if planthum + HUM_TOLERANCE < humtarget:
        hum_state = -1
    elif planthum - HUM_TOLERANCE  > humtarget:
        hum_state = 1

    if plantmoist + MOIST_TOLERANCE < moisttarget:
        moist_state = -1
    elif plantmoist  - MOIST_TOLERANCE > moisttarget:
        moist_state = 1


    


    #result will be in this form (tempstate, humstate, moiststate)

    return (temp_state, hum_state, moist_state)