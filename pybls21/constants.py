# Coils
CL_POWER = 0
CL_Boost_MODE = 3
CL_BoostSWITCH_CTRL = 13
CL_RESET_FILTER_TIMER = 17
CL_RESET_ALARM = 18

# Holding registers
HR_MaxSPEED_MODE = 1
HR_SPEED_MODE = 2
HR_ManualSPEED = 17
HR_OPERATION_MODE = 43
HR_SetTEMP = 44

# Input registers
IR_CurTEMP_SuAirIn = 1
IR_CurTEMP_SuAirOut = 2
IR_CurRH_Int = 10
IR_SuRPM = 23
IR_ExRPM = 24
IR_StateFILTER = 31
IR_VerMAIN_FMW_start = 34
IR_VerMAIN_FMW_end = 36
IR_DeviceTYPE = 37
IR_ALARM = 38

# MaNi additions
IR_CurTEMP_ExAirIn = 3 # temperature for ingoing fresh air
IR_CurTEMP_ExAirOut = 4 # temperature for outgoing air
IR_CurFILTER_TIMER = 28 # days until filters needs cleaning (address 27 refers to hours&minutes)
IR_CurSuPRESS = 21 # air pressure for ingoing fresh air
IR_CurExPRESS = 22 # air pressure for outgoing air
# EO MaNi additions
