# Coils
CL_POWER              = 0
CL_Boost_MODE         = 3
CL_BoostSWITCH_CTRL   = 13
CL_RESET_FILTER_TIMER = 17
CL_RESET_ALARM        = 18
CL_TIMER              = 1  # main timer status
CL_WEEK               = 2  # schedule mode status

# Holding registers
HR_MaxSPEED_MODE           = 1
HR_SPEED_MODE              = 2
HR_ManualSPEED             = 17
HR_OPERATION_MODE          = 43
HR_SetTEMP                 = 44
HR_BYPASS_ROTOR_TYPE       = 57
HR_BYPASS_ROTOR_MODE       = 74
HR_BYPASS_ROTOR_SET_MANUAL = 75

# Input registers
IR_CurTEMP_SuAirIn   = 1  # Outdoor air, before pre-heating
IR_CurTEMP_SuAirOut  = 2  # Supply air, at unit outlet
IR_CurTEMP_ExAirIn   = 3  # Extract air (from the rooms), at unit inlet
IR_CurTEMP_ExAirOut  = 4  # Exhaust air (to the outside), at unit outlet
IR_CurRH_Int         = 10
IR_CurSuAirFLOW      = 19
IR_CurExAirFLOW      = 20
IR_CurSuPRESS        = 21  # Pressure in the supply air duct, Pa
IR_CurExPRESS        = 22  # Pressure in the extract air duct, Pa
IR_SuRPM             = 23
IR_ExRPM             = 24
IR_CurTIMER_TIME     = 25 # countdown of main timer (25 is minutes and seconds)
IR_CurTIMER_TIME_HRS = 26 # countdown of main timer (26 is hours)
IR_CurFILTER_TIMER_HRS_MIN = 27 # time until filters needs cleaning (High byte: hours, low byte: minutes)
IR_CurFILTER_TIMER_DAYS    = 28 # time until filters needs cleaning (days)
IR_TotalWorkingTime_HRS_MIN = 29 # total operation time of ventilation unit (High byte: hours, low byte: minutes)
IR_TotalWorkingTime_DAYS    = 30 # total operation time of ventilation unit (days)
IR_StateFILTER         = 31 # filter status (clean, error, replacement)
IR_CurWeekSpeed        = 32 # speed from current timeframe of schedule mode
IR_VerMAIN_FMW_start   = 34
IR_VerMAIN_FMW_end     = 36
IR_DeviceTYPE          = 37
IR_ALARM               = 38
IR_BYPASS_ROTOR_U      = 45
IR_BYPASS_ROTOR_STATUS = 51
IR_CurSuFanSPEED       = 52
IR_CurExFanSPEED       = 53