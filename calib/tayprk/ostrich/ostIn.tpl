# Ostrich configuration file
ProgramType  DDS
ModelExecutable ./run_model.sh
ObjectiveFunction gcop

PreserveBestModel ./save_best.sh
PreserveModelOutput no
OnObsError	-999

BeginFilePairs    
nc_multiplier.tpl; nc_multiplier.txt
EndFilePairs

#Parameter/DV Specification
BeginParams
#parameter			init	lwr	upr	txInN  txOst 	txOut fmt  
k_macropore_mtp			1.0	lwr	upr	none   none	none  F9.4
k_soil_mtp			1.0	lwr	upr	none   none	none  F9.4
theta_sat_mtp			1.0	lwr	upr	none   none	none  F9.4
basin__aquiferBaseflowExp_mtp	1.0	lwr	upr	none   none	none  F9.4
basin__aquiferHydCond_mtp	1.0	lwr	upr	none   none	none  F9.4
qSurfScale_mtp			1.0	lwr	upr	none   none	none  F9.4
summerLAI_mtp			1.0	lwr	upr	none   none	none  F9.4	
frozenPrecipMultip_mtp		1.0	lwr	upr	none   none	none  F9.4	
EndParams

BeginResponseVars
  #name	  filename			      keyword		line	col	token
  KGE      ./model/Diagnostics.txt;	      OST_NULL	         1	1  	 ' '
EndResponseVars 

BeginTiedRespVars
  NegKGE 1 KGE wsum -1.00
EndTiedRespVars

BeginGCOP
  CostFunction NegKGE
  PenaltyFunction APM
EndGCOP

BeginConstraints
# not needed when no constraints, but PenaltyFunction statement above is required
# name     type     penalty    lwr   upr   resp.var
EndConstraints

BeginDDSAlg
PerturbationValue 0.20
MaxIterations 200
#UseRandomParamValues
UseInitialParamValues
EndDDSAlg

# can attempt this to polish the earlier DDS results (use with WARM start)
#BeginFletchReevesAlg
#ConvergenceVal 1.00E-6
#MaxStalls      3
#MaxIterations  20
#EndFletchReevesAlg
