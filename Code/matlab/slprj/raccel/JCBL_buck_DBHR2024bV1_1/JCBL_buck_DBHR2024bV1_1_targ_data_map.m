    function targMap = targDataMap(),

    ;%***********************
    ;% Create Parameter Map *
    ;%***********************
    
        nTotData      = 0; %add to this count as we go
        nTotSects     = 43;
        sectIdxOffset = 0;

        ;%
        ;% Define dummy sections & preallocate arrays
        ;%
        dumSection.nData = -1;
        dumSection.data  = [];

        dumData.logicalSrcIdx = -1;
        dumData.dtTransOffset = -1;

        ;%
        ;% Init/prealloc paramMap
        ;%
        paramMap.nSections           = nTotSects;
        paramMap.sectIdxOffset       = sectIdxOffset;
            paramMap.sections(nTotSects) = dumSection; %prealloc
        paramMap.nTotData            = -1;

        ;%
        ;% Auto data (rtP)
        ;%
            section.nData     = 35;
            section.data(35)  = dumData; %prealloc

                    ;% rtP.DC_Source_Amplitude
                    section.data(1).logicalSrcIdx = 0;
                    section.data(1).dtTransOffset = 0;

                    ;% rtP.OnDelay1_DelayType
                    section.data(2).logicalSrcIdx = 1;
                    section.data(2).dtTransOffset = 1;

                    ;% rtP.OnDelay2_DelayType
                    section.data(3).logicalSrcIdx = 2;
                    section.data(3).dtTransOffset = 2;

                    ;% rtP.OnDelay3_DelayType
                    section.data(4).logicalSrcIdx = 3;
                    section.data(4).dtTransOffset = 3;

                    ;% rtP.OnDelay4_DelayType
                    section.data(5).logicalSrcIdx = 4;
                    section.data(5).dtTransOffset = 4;

                    ;% rtP.PowerMeasurement1_F
                    section.data(6).logicalSrcIdx = 5;
                    section.data(6).dtTransOffset = 5;

                    ;% rtP.PowerMeasurement_F
                    section.data(7).logicalSrcIdx = 6;
                    section.data(7).dtTransOffset = 6;

                    ;% rtP.PIDController2_I
                    section.data(8).logicalSrcIdx = 7;
                    section.data(8).dtTransOffset = 7;

                    ;% rtP.PIDController3_I
                    section.data(9).logicalSrcIdx = 8;
                    section.data(9).dtTransOffset = 8;

                    ;% rtP.PIDController4_I
                    section.data(10).logicalSrcIdx = 9;
                    section.data(10).dtTransOffset = 9;

                    ;% rtP.PIDController3_InitialConditionForIntegrator
                    section.data(11).logicalSrcIdx = 10;
                    section.data(11).dtTransOffset = 10;

                    ;% rtP.PIDController2_InitialConditionForIntegrator
                    section.data(12).logicalSrcIdx = 11;
                    section.data(12).dtTransOffset = 11;

                    ;% rtP.PIDController4_InitialConditionForIntegrator
                    section.data(13).logicalSrcIdx = 12;
                    section.data(13).dtTransOffset = 12;

                    ;% rtP.Ramp_InitialOutput
                    section.data(14).logicalSrcIdx = 13;
                    section.data(14).dtTransOffset = 13;

                    ;% rtP.PowerMeasurement1_K
                    section.data(15).logicalSrcIdx = 14;
                    section.data(15).dtTransOffset = 14;

                    ;% rtP.PowerMeasurement_K
                    section.data(16).logicalSrcIdx = 15;
                    section.data(16).dtTransOffset = 15;

                    ;% rtP.PIDController3_LowerSaturationLimit
                    section.data(17).logicalSrcIdx = 16;
                    section.data(17).dtTransOffset = 16;

                    ;% rtP.PIDController2_LowerSaturationLimit
                    section.data(18).logicalSrcIdx = 17;
                    section.data(18).dtTransOffset = 17;

                    ;% rtP.PIDController4_LowerSaturationLimit
                    section.data(19).logicalSrcIdx = 18;
                    section.data(19).dtTransOffset = 18;

                    ;% rtP.PIDController3_P
                    section.data(20).logicalSrcIdx = 19;
                    section.data(20).dtTransOffset = 19;

                    ;% rtP.PIDController2_P
                    section.data(21).logicalSrcIdx = 20;
                    section.data(21).dtTransOffset = 20;

                    ;% rtP.PIDController4_P
                    section.data(22).logicalSrcIdx = 21;
                    section.data(22).dtTransOffset = 21;

                    ;% rtP.PIDController3_UpperSaturationLimit
                    section.data(23).logicalSrcIdx = 22;
                    section.data(23).dtTransOffset = 22;

                    ;% rtP.PIDController2_UpperSaturationLimit
                    section.data(24).logicalSrcIdx = 23;
                    section.data(24).dtTransOffset = 23;

                    ;% rtP.PIDController4_UpperSaturationLimit
                    section.data(25).logicalSrcIdx = 24;
                    section.data(25).dtTransOffset = 24;

                    ;% rtP.OnDelay1_delay
                    section.data(26).logicalSrcIdx = 25;
                    section.data(26).dtTransOffset = 25;

                    ;% rtP.OnDelay2_delay
                    section.data(27).logicalSrcIdx = 26;
                    section.data(27).dtTransOffset = 26;

                    ;% rtP.OnDelay3_delay
                    section.data(28).logicalSrcIdx = 27;
                    section.data(28).dtTransOffset = 27;

                    ;% rtP.OnDelay4_delay
                    section.data(29).logicalSrcIdx = 28;
                    section.data(29).dtTransOffset = 28;

                    ;% rtP.RepeatingSequence1_rep_seq_y
                    section.data(30).logicalSrcIdx = 29;
                    section.data(30).dtTransOffset = 29;

                    ;% rtP.RepeatingSequence2_rep_seq_y
                    section.data(31).logicalSrcIdx = 30;
                    section.data(31).dtTransOffset = 32;

                    ;% rtP.Ramp_slope
                    section.data(32).logicalSrcIdx = 31;
                    section.data(32).dtTransOffset = 35;

                    ;% rtP.Ramp_start
                    section.data(33).logicalSrcIdx = 32;
                    section.data(33).dtTransOffset = 36;

                    ;% rtP.IntegratorwithWrappedStateDiscreteorContinuous_x0
                    section.data(34).logicalSrcIdx = 33;
                    section.data(34).dtTransOffset = 37;

                    ;% rtP.IntegratorwithWrappedStateDiscreteorContinuous_x0_ho2g52dycf
                    section.data(35).logicalSrcIdx = 34;
                    section.data(35).dtTransOffset = 38;

            nTotData = nTotData + section.nData;
            paramMap.sections(1) = section;
            clear section

            section.nData     = 4;
            section.data(4)  = dumData; %prealloc

                    ;% rtP.OnDelay2_ic
                    section.data(1).logicalSrcIdx = 35;
                    section.data(1).dtTransOffset = 0;

                    ;% rtP.OnDelay1_ic
                    section.data(2).logicalSrcIdx = 36;
                    section.data(2).dtTransOffset = 1;

                    ;% rtP.OnDelay3_ic
                    section.data(3).logicalSrcIdx = 37;
                    section.data(3).dtTransOffset = 2;

                    ;% rtP.OnDelay4_ic
                    section.data(4).logicalSrcIdx = 38;
                    section.data(4).dtTransOffset = 3;

            nTotData = nTotData + section.nData;
            paramMap.sections(2) = section;
            clear section

            section.nData     = 50;
            section.data(50)  = dumData; %prealloc

                    ;% rtP.Gain_Gain
                    section.data(1).logicalSrcIdx = 39;
                    section.data(1).dtTransOffset = 0;

                    ;% rtP.Step_Time
                    section.data(2).logicalSrcIdx = 40;
                    section.data(2).dtTransOffset = 1;

                    ;% rtP.Step_Y0
                    section.data(3).logicalSrcIdx = 41;
                    section.data(3).dtTransOffset = 2;

                    ;% rtP.Step_YFinal
                    section.data(4).logicalSrcIdx = 42;
                    section.data(4).dtTransOffset = 3;

                    ;% rtP.StateSpace_AS_param
                    section.data(5).logicalSrcIdx = 43;
                    section.data(5).dtTransOffset = 4;

                    ;% rtP.StateSpace_BS_param
                    section.data(6).logicalSrcIdx = 44;
                    section.data(6).dtTransOffset = 13;

                    ;% rtP.StateSpace_CS_param
                    section.data(7).logicalSrcIdx = 45;
                    section.data(7).dtTransOffset = 46;

                    ;% rtP.StateSpace_DS_param
                    section.data(8).logicalSrcIdx = 46;
                    section.data(8).dtTransOffset = 94;

                    ;% rtP.StateSpace_X0_param
                    section.data(9).logicalSrcIdx = 47;
                    section.data(9).dtTransOffset = 270;

                    ;% rtP.donotdeletethisgain_Gain
                    section.data(10).logicalSrcIdx = 48;
                    section.data(10).dtTransOffset = 273;

                    ;% rtP.donotdeletethisgain_Gain_gvfqsabyx1
                    section.data(11).logicalSrcIdx = 49;
                    section.data(11).dtTransOffset = 274;

                    ;% rtP.Step_Y0_lxbncpeaoj
                    section.data(12).logicalSrcIdx = 50;
                    section.data(12).dtTransOffset = 275;

                    ;% rtP.Saturation4_UpperSat
                    section.data(13).logicalSrcIdx = 51;
                    section.data(13).dtTransOffset = 276;

                    ;% rtP.Saturation4_LowerSat
                    section.data(14).logicalSrcIdx = 52;
                    section.data(14).dtTransOffset = 277;

                    ;% rtP.donotdeletethisgain_Gain_jhwfhqwbws
                    section.data(15).logicalSrcIdx = 53;
                    section.data(15).dtTransOffset = 278;

                    ;% rtP.donotdeletethisgain_Gain_nqt4qtawxo
                    section.data(16).logicalSrcIdx = 54;
                    section.data(16).dtTransOffset = 279;

                    ;% rtP.Saturation1_UpperSat
                    section.data(17).logicalSrcIdx = 55;
                    section.data(17).dtTransOffset = 280;

                    ;% rtP.Saturation1_LowerSat
                    section.data(18).logicalSrcIdx = 56;
                    section.data(18).dtTransOffset = 281;

                    ;% rtP.LookUpTable1_bp01Data
                    section.data(19).logicalSrcIdx = 57;
                    section.data(19).dtTransOffset = 282;

                    ;% rtP.Saturation2_UpperSat
                    section.data(20).logicalSrcIdx = 58;
                    section.data(20).dtTransOffset = 285;

                    ;% rtP.Saturation2_LowerSat
                    section.data(21).logicalSrcIdx = 59;
                    section.data(21).dtTransOffset = 286;

                    ;% rtP.LookUpTable1_bp01Data_b1l1rtt4v4
                    section.data(22).logicalSrcIdx = 60;
                    section.data(22).dtTransOffset = 287;

                    ;% rtP.Integrator_IC
                    section.data(23).logicalSrcIdx = 61;
                    section.data(23).dtTransOffset = 290;

                    ;% rtP.TransportDelay_InitOutput
                    section.data(24).logicalSrcIdx = 62;
                    section.data(24).dtTransOffset = 291;

                    ;% rtP.Integrator1_IC
                    section.data(25).logicalSrcIdx = 63;
                    section.data(25).dtTransOffset = 292;

                    ;% rtP.TransportDelay1_InitOutput
                    section.data(26).logicalSrcIdx = 64;
                    section.data(26).dtTransOffset = 293;

                    ;% rtP.Gain2_Gain
                    section.data(27).logicalSrcIdx = 65;
                    section.data(27).dtTransOffset = 294;

                    ;% rtP.integrator_IC
                    section.data(28).logicalSrcIdx = 66;
                    section.data(28).dtTransOffset = 295;

                    ;% rtP.TransportDelay_Delay
                    section.data(29).logicalSrcIdx = 67;
                    section.data(29).dtTransOffset = 296;

                    ;% rtP.TransportDelay_InitOutput_kicmfwddcc
                    section.data(30).logicalSrcIdx = 68;
                    section.data(30).dtTransOffset = 297;

                    ;% rtP.K1_Value
                    section.data(31).logicalSrcIdx = 69;
                    section.data(31).dtTransOffset = 298;

                    ;% rtP.Memory_InitialCondition
                    section.data(32).logicalSrcIdx = 70;
                    section.data(32).dtTransOffset = 299;

                    ;% rtP.donotdeletethisgain_Gain_j53zpnfq1l
                    section.data(33).logicalSrcIdx = 71;
                    section.data(33).dtTransOffset = 300;

                    ;% rtP.donotdeletethisgain_Gain_j1rbetrqjl
                    section.data(34).logicalSrcIdx = 72;
                    section.data(34).dtTransOffset = 301;

                    ;% rtP.Integrator_IC_pcacovp33f
                    section.data(35).logicalSrcIdx = 73;
                    section.data(35).dtTransOffset = 302;

                    ;% rtP.TransportDelay_InitOutput_fombx3et2x
                    section.data(36).logicalSrcIdx = 74;
                    section.data(36).dtTransOffset = 303;

                    ;% rtP.Integrator1_IC_djc22nftrb
                    section.data(37).logicalSrcIdx = 75;
                    section.data(37).dtTransOffset = 304;

                    ;% rtP.TransportDelay1_InitOutput_mtvo3uiixw
                    section.data(38).logicalSrcIdx = 76;
                    section.data(38).dtTransOffset = 305;

                    ;% rtP.Gain2_Gain_ofybcmyjpl
                    section.data(39).logicalSrcIdx = 77;
                    section.data(39).dtTransOffset = 306;

                    ;% rtP.donotdeletethisgain_Gain_h2u25h3cgt
                    section.data(40).logicalSrcIdx = 78;
                    section.data(40).dtTransOffset = 307;

                    ;% rtP.Step1_Time
                    section.data(41).logicalSrcIdx = 79;
                    section.data(41).dtTransOffset = 308;

                    ;% rtP.Step1_Y0
                    section.data(42).logicalSrcIdx = 80;
                    section.data(42).dtTransOffset = 309;

                    ;% rtP.Step1_YFinal
                    section.data(43).logicalSrcIdx = 81;
                    section.data(43).dtTransOffset = 310;

                    ;% rtP.SwitchCurrents_Value
                    section.data(44).logicalSrcIdx = 82;
                    section.data(44).dtTransOffset = 311;

                    ;% rtP.Constant_Value
                    section.data(45).logicalSrcIdx = 83;
                    section.data(45).dtTransOffset = 320;

                    ;% rtP.Constant_Value_aafub0ppks
                    section.data(46).logicalSrcIdx = 84;
                    section.data(46).dtTransOffset = 321;

                    ;% rtP.Constant_Value_bt2nl4rme1
                    section.data(47).logicalSrcIdx = 85;
                    section.data(47).dtTransOffset = 322;

                    ;% rtP.Constant_Value_f3ddoxps25
                    section.data(48).logicalSrcIdx = 86;
                    section.data(48).dtTransOffset = 323;

                    ;% rtP.Constant_Value_bkksiov2pm
                    section.data(49).logicalSrcIdx = 87;
                    section.data(49).dtTransOffset = 324;

                    ;% rtP.Constant_Value_ld5luqozqd
                    section.data(50).logicalSrcIdx = 88;
                    section.data(50).dtTransOffset = 325;

            nTotData = nTotData + section.nData;
            paramMap.sections(3) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtP.onbve342oz.SampleandHold_ic
                    section.data(1).logicalSrcIdx = 89;
                    section.data(1).dtTransOffset = 0;

                    ;% rtP.onbve342oz.EdgeDetector_model
                    section.data(2).logicalSrcIdx = 90;
                    section.data(2).dtTransOffset = 1;

                    ;% rtP.onbve342oz.Constant_Value
                    section.data(3).logicalSrcIdx = 91;
                    section.data(3).dtTransOffset = 2;

                    ;% rtP.onbve342oz.posedge_Value
                    section.data(4).logicalSrcIdx = 92;
                    section.data(4).dtTransOffset = 3;

                    ;% rtP.onbve342oz.negedge_Value
                    section.data(5).logicalSrcIdx = 93;
                    section.data(5).dtTransOffset = 5;

                    ;% rtP.onbve342oz.eitheredge_Value
                    section.data(6).logicalSrcIdx = 94;
                    section.data(6).dtTransOffset = 7;

            nTotData = nTotData + section.nData;
            paramMap.sections(4) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.onbve342oz.OUT_Y0
                    section.data(1).logicalSrcIdx = 95;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(5) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.onbve342oz.hdj3wqdohr.OUT_Y0
                    section.data(1).logicalSrcIdx = 96;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(6) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.onbve342oz.em1ujbr42u.OUT_Y0
                    section.data(1).logicalSrcIdx = 97;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(7) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.onbve342oz.gg21spqnj5.Out1_Y0
                    section.data(1).logicalSrcIdx = 98;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(8) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtP.i4guox0dks.SampleandHold_ic
                    section.data(1).logicalSrcIdx = 99;
                    section.data(1).dtTransOffset = 0;

                    ;% rtP.i4guox0dks.EdgeDetector_model
                    section.data(2).logicalSrcIdx = 100;
                    section.data(2).dtTransOffset = 1;

                    ;% rtP.i4guox0dks.Constant_Value
                    section.data(3).logicalSrcIdx = 101;
                    section.data(3).dtTransOffset = 2;

                    ;% rtP.i4guox0dks.posedge_Value
                    section.data(4).logicalSrcIdx = 102;
                    section.data(4).dtTransOffset = 3;

                    ;% rtP.i4guox0dks.negedge_Value
                    section.data(5).logicalSrcIdx = 103;
                    section.data(5).dtTransOffset = 5;

                    ;% rtP.i4guox0dks.eitheredge_Value
                    section.data(6).logicalSrcIdx = 104;
                    section.data(6).dtTransOffset = 7;

            nTotData = nTotData + section.nData;
            paramMap.sections(9) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.i4guox0dks.OUT_Y0
                    section.data(1).logicalSrcIdx = 105;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(10) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.i4guox0dks.ke0ovyvkjxg.OUT_Y0
                    section.data(1).logicalSrcIdx = 106;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(11) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.i4guox0dks.cg52ak5rbj5.OUT_Y0
                    section.data(1).logicalSrcIdx = 107;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(12) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.i4guox0dks.bkqbq1qpitt.Out1_Y0
                    section.data(1).logicalSrcIdx = 108;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(13) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtP.awk1sqt1lf.SampleandHold_ic
                    section.data(1).logicalSrcIdx = 109;
                    section.data(1).dtTransOffset = 0;

                    ;% rtP.awk1sqt1lf.EdgeDetector_model
                    section.data(2).logicalSrcIdx = 110;
                    section.data(2).dtTransOffset = 1;

                    ;% rtP.awk1sqt1lf.Constant_Value
                    section.data(3).logicalSrcIdx = 111;
                    section.data(3).dtTransOffset = 2;

                    ;% rtP.awk1sqt1lf.posedge_Value
                    section.data(4).logicalSrcIdx = 112;
                    section.data(4).dtTransOffset = 3;

                    ;% rtP.awk1sqt1lf.negedge_Value
                    section.data(5).logicalSrcIdx = 113;
                    section.data(5).dtTransOffset = 5;

                    ;% rtP.awk1sqt1lf.eitheredge_Value
                    section.data(6).logicalSrcIdx = 114;
                    section.data(6).dtTransOffset = 7;

            nTotData = nTotData + section.nData;
            paramMap.sections(14) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.awk1sqt1lf.OUT_Y0
                    section.data(1).logicalSrcIdx = 115;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(15) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.awk1sqt1lf.hdj3wqdohr.OUT_Y0
                    section.data(1).logicalSrcIdx = 116;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(16) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.awk1sqt1lf.em1ujbr42u.OUT_Y0
                    section.data(1).logicalSrcIdx = 117;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(17) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.awk1sqt1lf.gg21spqnj5.Out1_Y0
                    section.data(1).logicalSrcIdx = 118;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(18) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtP.hquvqsfosa.SampleandHold_ic
                    section.data(1).logicalSrcIdx = 119;
                    section.data(1).dtTransOffset = 0;

                    ;% rtP.hquvqsfosa.EdgeDetector_model
                    section.data(2).logicalSrcIdx = 120;
                    section.data(2).dtTransOffset = 1;

                    ;% rtP.hquvqsfosa.Constant_Value
                    section.data(3).logicalSrcIdx = 121;
                    section.data(3).dtTransOffset = 2;

                    ;% rtP.hquvqsfosa.posedge_Value
                    section.data(4).logicalSrcIdx = 122;
                    section.data(4).dtTransOffset = 3;

                    ;% rtP.hquvqsfosa.negedge_Value
                    section.data(5).logicalSrcIdx = 123;
                    section.data(5).dtTransOffset = 5;

                    ;% rtP.hquvqsfosa.eitheredge_Value
                    section.data(6).logicalSrcIdx = 124;
                    section.data(6).dtTransOffset = 7;

            nTotData = nTotData + section.nData;
            paramMap.sections(19) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.hquvqsfosa.OUT_Y0
                    section.data(1).logicalSrcIdx = 125;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(20) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.hquvqsfosa.ke0ovyvkjxg.OUT_Y0
                    section.data(1).logicalSrcIdx = 126;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(21) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.hquvqsfosa.cg52ak5rbj5.OUT_Y0
                    section.data(1).logicalSrcIdx = 127;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(22) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.hquvqsfosa.bkqbq1qpitt.Out1_Y0
                    section.data(1).logicalSrcIdx = 128;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(23) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtP.hm4diydndl.SampleandHold_ic
                    section.data(1).logicalSrcIdx = 129;
                    section.data(1).dtTransOffset = 0;

                    ;% rtP.hm4diydndl.EdgeDetector_model
                    section.data(2).logicalSrcIdx = 130;
                    section.data(2).dtTransOffset = 1;

                    ;% rtP.hm4diydndl.Constant_Value
                    section.data(3).logicalSrcIdx = 131;
                    section.data(3).dtTransOffset = 2;

                    ;% rtP.hm4diydndl.posedge_Value
                    section.data(4).logicalSrcIdx = 132;
                    section.data(4).dtTransOffset = 3;

                    ;% rtP.hm4diydndl.negedge_Value
                    section.data(5).logicalSrcIdx = 133;
                    section.data(5).dtTransOffset = 5;

                    ;% rtP.hm4diydndl.eitheredge_Value
                    section.data(6).logicalSrcIdx = 134;
                    section.data(6).dtTransOffset = 7;

            nTotData = nTotData + section.nData;
            paramMap.sections(24) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.hm4diydndl.OUT_Y0
                    section.data(1).logicalSrcIdx = 135;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(25) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.hm4diydndl.hdj3wqdohr.OUT_Y0
                    section.data(1).logicalSrcIdx = 136;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(26) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.hm4diydndl.em1ujbr42u.OUT_Y0
                    section.data(1).logicalSrcIdx = 137;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(27) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.hm4diydndl.gg21spqnj5.Out1_Y0
                    section.data(1).logicalSrcIdx = 138;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(28) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtP.do3rpmepfq.SampleandHold_ic
                    section.data(1).logicalSrcIdx = 139;
                    section.data(1).dtTransOffset = 0;

                    ;% rtP.do3rpmepfq.EdgeDetector_model
                    section.data(2).logicalSrcIdx = 140;
                    section.data(2).dtTransOffset = 1;

                    ;% rtP.do3rpmepfq.Constant_Value
                    section.data(3).logicalSrcIdx = 141;
                    section.data(3).dtTransOffset = 2;

                    ;% rtP.do3rpmepfq.posedge_Value
                    section.data(4).logicalSrcIdx = 142;
                    section.data(4).dtTransOffset = 3;

                    ;% rtP.do3rpmepfq.negedge_Value
                    section.data(5).logicalSrcIdx = 143;
                    section.data(5).dtTransOffset = 5;

                    ;% rtP.do3rpmepfq.eitheredge_Value
                    section.data(6).logicalSrcIdx = 144;
                    section.data(6).dtTransOffset = 7;

            nTotData = nTotData + section.nData;
            paramMap.sections(29) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.do3rpmepfq.OUT_Y0
                    section.data(1).logicalSrcIdx = 145;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(30) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.do3rpmepfq.ke0ovyvkjxg.OUT_Y0
                    section.data(1).logicalSrcIdx = 146;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(31) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.do3rpmepfq.cg52ak5rbj5.OUT_Y0
                    section.data(1).logicalSrcIdx = 147;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(32) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.do3rpmepfq.bkqbq1qpitt.Out1_Y0
                    section.data(1).logicalSrcIdx = 148;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(33) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtP.loki5osupmm.SampleandHold_ic
                    section.data(1).logicalSrcIdx = 149;
                    section.data(1).dtTransOffset = 0;

                    ;% rtP.loki5osupmm.EdgeDetector_model
                    section.data(2).logicalSrcIdx = 150;
                    section.data(2).dtTransOffset = 1;

                    ;% rtP.loki5osupmm.Constant_Value
                    section.data(3).logicalSrcIdx = 151;
                    section.data(3).dtTransOffset = 2;

                    ;% rtP.loki5osupmm.posedge_Value
                    section.data(4).logicalSrcIdx = 152;
                    section.data(4).dtTransOffset = 3;

                    ;% rtP.loki5osupmm.negedge_Value
                    section.data(5).logicalSrcIdx = 153;
                    section.data(5).dtTransOffset = 5;

                    ;% rtP.loki5osupmm.eitheredge_Value
                    section.data(6).logicalSrcIdx = 154;
                    section.data(6).dtTransOffset = 7;

            nTotData = nTotData + section.nData;
            paramMap.sections(34) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.loki5osupmm.OUT_Y0
                    section.data(1).logicalSrcIdx = 155;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(35) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.loki5osupmm.hdj3wqdohr.OUT_Y0
                    section.data(1).logicalSrcIdx = 156;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(36) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.loki5osupmm.em1ujbr42u.OUT_Y0
                    section.data(1).logicalSrcIdx = 157;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(37) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.loki5osupmm.gg21spqnj5.Out1_Y0
                    section.data(1).logicalSrcIdx = 158;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(38) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtP.nvd5ofuthxp.SampleandHold_ic
                    section.data(1).logicalSrcIdx = 159;
                    section.data(1).dtTransOffset = 0;

                    ;% rtP.nvd5ofuthxp.EdgeDetector_model
                    section.data(2).logicalSrcIdx = 160;
                    section.data(2).dtTransOffset = 1;

                    ;% rtP.nvd5ofuthxp.Constant_Value
                    section.data(3).logicalSrcIdx = 161;
                    section.data(3).dtTransOffset = 2;

                    ;% rtP.nvd5ofuthxp.posedge_Value
                    section.data(4).logicalSrcIdx = 162;
                    section.data(4).dtTransOffset = 3;

                    ;% rtP.nvd5ofuthxp.negedge_Value
                    section.data(5).logicalSrcIdx = 163;
                    section.data(5).dtTransOffset = 5;

                    ;% rtP.nvd5ofuthxp.eitheredge_Value
                    section.data(6).logicalSrcIdx = 164;
                    section.data(6).dtTransOffset = 7;

            nTotData = nTotData + section.nData;
            paramMap.sections(39) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.nvd5ofuthxp.OUT_Y0
                    section.data(1).logicalSrcIdx = 165;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(40) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.nvd5ofuthxp.ke0ovyvkjxg.OUT_Y0
                    section.data(1).logicalSrcIdx = 166;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(41) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.nvd5ofuthxp.cg52ak5rbj5.OUT_Y0
                    section.data(1).logicalSrcIdx = 167;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(42) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtP.nvd5ofuthxp.bkqbq1qpitt.Out1_Y0
                    section.data(1).logicalSrcIdx = 168;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            paramMap.sections(43) = section;
            clear section


            ;%
            ;% Non-auto Data (parameter)
            ;%


        ;%
        ;% Add final counts to struct.
        ;%
        paramMap.nTotData = nTotData;



    ;%**************************
    ;% Create Block Output Map *
    ;%**************************
    
        nTotData      = 0; %add to this count as we go
        nTotSects     = 43;
        sectIdxOffset = 0;

        ;%
        ;% Define dummy sections & preallocate arrays
        ;%
        dumSection.nData = -1;
        dumSection.data  = [];

        dumData.logicalSrcIdx = -1;
        dumData.dtTransOffset = -1;

        ;%
        ;% Init/prealloc sigMap
        ;%
        sigMap.nSections           = nTotSects;
        sigMap.sectIdxOffset       = sectIdxOffset;
            sigMap.sections(nTotSects) = dumSection; %prealloc
        sigMap.nTotData            = -1;

        ;%
        ;% Auto data (rtB)
        ;%
            section.nData     = 4;
            section.data(4)  = dumData; %prealloc

                    ;% rtB.dnp4xhqtmm
                    section.data(1).logicalSrcIdx = 0;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.anl0tg4iz1
                    section.data(2).logicalSrcIdx = 1;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.n543rgdc5p
                    section.data(3).logicalSrcIdx = 2;
                    section.data(3).dtTransOffset = 2;

                    ;% rtB.it5skppvd3
                    section.data(4).logicalSrcIdx = 3;
                    section.data(4).dtTransOffset = 3;

            nTotData = nTotData + section.nData;
            sigMap.sections(1) = section;
            clear section

            section.nData     = 66;
            section.data(66)  = dumData; %prealloc

                    ;% rtB.abpfnsf1za
                    section.data(1).logicalSrcIdx = 4;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.lkdwg1e5as
                    section.data(2).logicalSrcIdx = 5;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.hysz5xbpi4
                    section.data(3).logicalSrcIdx = 6;
                    section.data(3).dtTransOffset = 17;

                    ;% rtB.k304e1ffaf
                    section.data(4).logicalSrcIdx = 7;
                    section.data(4).dtTransOffset = 26;

                    ;% rtB.coe52itnyj
                    section.data(5).logicalSrcIdx = 8;
                    section.data(5).dtTransOffset = 27;

                    ;% rtB.ofgigatwme
                    section.data(6).logicalSrcIdx = 9;
                    section.data(6).dtTransOffset = 28;

                    ;% rtB.ew24g1cq3f
                    section.data(7).logicalSrcIdx = 10;
                    section.data(7).dtTransOffset = 29;

                    ;% rtB.eg2ebhj1nk
                    section.data(8).logicalSrcIdx = 11;
                    section.data(8).dtTransOffset = 30;

                    ;% rtB.mtjhreoifs
                    section.data(9).logicalSrcIdx = 12;
                    section.data(9).dtTransOffset = 31;

                    ;% rtB.m5ryk3hdiv
                    section.data(10).logicalSrcIdx = 13;
                    section.data(10).dtTransOffset = 32;

                    ;% rtB.gzp23yd1xv
                    section.data(11).logicalSrcIdx = 14;
                    section.data(11).dtTransOffset = 33;

                    ;% rtB.cwz10fldst
                    section.data(12).logicalSrcIdx = 15;
                    section.data(12).dtTransOffset = 34;

                    ;% rtB.bfyozmv3px
                    section.data(13).logicalSrcIdx = 16;
                    section.data(13).dtTransOffset = 35;

                    ;% rtB.pbyyfznmio
                    section.data(14).logicalSrcIdx = 17;
                    section.data(14).dtTransOffset = 36;

                    ;% rtB.myg5swu2wb
                    section.data(15).logicalSrcIdx = 18;
                    section.data(15).dtTransOffset = 37;

                    ;% rtB.ioi1uyv1fn
                    section.data(16).logicalSrcIdx = 19;
                    section.data(16).dtTransOffset = 38;

                    ;% rtB.nmcbo1u1cf
                    section.data(17).logicalSrcIdx = 20;
                    section.data(17).dtTransOffset = 39;

                    ;% rtB.ge4lifbpj5
                    section.data(18).logicalSrcIdx = 21;
                    section.data(18).dtTransOffset = 40;

                    ;% rtB.mv4hqtekcz
                    section.data(19).logicalSrcIdx = 22;
                    section.data(19).dtTransOffset = 41;

                    ;% rtB.mwezxuddk0
                    section.data(20).logicalSrcIdx = 23;
                    section.data(20).dtTransOffset = 42;

                    ;% rtB.dietul3zsf
                    section.data(21).logicalSrcIdx = 24;
                    section.data(21).dtTransOffset = 43;

                    ;% rtB.by5zad2onw
                    section.data(22).logicalSrcIdx = 25;
                    section.data(22).dtTransOffset = 44;

                    ;% rtB.cyzbgyotev
                    section.data(23).logicalSrcIdx = 26;
                    section.data(23).dtTransOffset = 45;

                    ;% rtB.jsczkkzz2y
                    section.data(24).logicalSrcIdx = 27;
                    section.data(24).dtTransOffset = 46;

                    ;% rtB.di13widl00
                    section.data(25).logicalSrcIdx = 28;
                    section.data(25).dtTransOffset = 47;

                    ;% rtB.hfzwclvxzm
                    section.data(26).logicalSrcIdx = 29;
                    section.data(26).dtTransOffset = 48;

                    ;% rtB.fxxy1ey0fk
                    section.data(27).logicalSrcIdx = 30;
                    section.data(27).dtTransOffset = 49;

                    ;% rtB.oigfmvncad
                    section.data(28).logicalSrcIdx = 31;
                    section.data(28).dtTransOffset = 50;

                    ;% rtB.jpsto2dx5g
                    section.data(29).logicalSrcIdx = 32;
                    section.data(29).dtTransOffset = 51;

                    ;% rtB.ahxbcbdnrs
                    section.data(30).logicalSrcIdx = 33;
                    section.data(30).dtTransOffset = 52;

                    ;% rtB.dawhtu05zh
                    section.data(31).logicalSrcIdx = 34;
                    section.data(31).dtTransOffset = 54;

                    ;% rtB.cbzs3aoi33
                    section.data(32).logicalSrcIdx = 35;
                    section.data(32).dtTransOffset = 56;

                    ;% rtB.i4ldxcfyv0
                    section.data(33).logicalSrcIdx = 36;
                    section.data(33).dtTransOffset = 57;

                    ;% rtB.fem1cpj0o2
                    section.data(34).logicalSrcIdx = 37;
                    section.data(34).dtTransOffset = 58;

                    ;% rtB.flbmpvq24q
                    section.data(35).logicalSrcIdx = 38;
                    section.data(35).dtTransOffset = 59;

                    ;% rtB.gn2zf0jpxq
                    section.data(36).logicalSrcIdx = 39;
                    section.data(36).dtTransOffset = 60;

                    ;% rtB.hx5fnaaum0
                    section.data(37).logicalSrcIdx = 40;
                    section.data(37).dtTransOffset = 61;

                    ;% rtB.oiwfgog0k1
                    section.data(38).logicalSrcIdx = 41;
                    section.data(38).dtTransOffset = 62;

                    ;% rtB.cr5skyilwh
                    section.data(39).logicalSrcIdx = 42;
                    section.data(39).dtTransOffset = 63;

                    ;% rtB.lgogrse5na
                    section.data(40).logicalSrcIdx = 43;
                    section.data(40).dtTransOffset = 64;

                    ;% rtB.c5byjgqb1r
                    section.data(41).logicalSrcIdx = 44;
                    section.data(41).dtTransOffset = 65;

                    ;% rtB.cixybdmuda
                    section.data(42).logicalSrcIdx = 45;
                    section.data(42).dtTransOffset = 66;

                    ;% rtB.cg4fkviq31
                    section.data(43).logicalSrcIdx = 46;
                    section.data(43).dtTransOffset = 67;

                    ;% rtB.f5ahwbuvym
                    section.data(44).logicalSrcIdx = 47;
                    section.data(44).dtTransOffset = 68;

                    ;% rtB.ekktospgws
                    section.data(45).logicalSrcIdx = 48;
                    section.data(45).dtTransOffset = 69;

                    ;% rtB.jtdtjsfqec
                    section.data(46).logicalSrcIdx = 49;
                    section.data(46).dtTransOffset = 71;

                    ;% rtB.pjqaf5khvb
                    section.data(47).logicalSrcIdx = 50;
                    section.data(47).dtTransOffset = 73;

                    ;% rtB.ekadme4enf
                    section.data(48).logicalSrcIdx = 51;
                    section.data(48).dtTransOffset = 74;

                    ;% rtB.py0xumfzpu
                    section.data(49).logicalSrcIdx = 52;
                    section.data(49).dtTransOffset = 75;

                    ;% rtB.pp00h1aqqk
                    section.data(50).logicalSrcIdx = 53;
                    section.data(50).dtTransOffset = 76;

                    ;% rtB.ddt1xyv13a
                    section.data(51).logicalSrcIdx = 54;
                    section.data(51).dtTransOffset = 77;

                    ;% rtB.f5bpgag2mb
                    section.data(52).logicalSrcIdx = 55;
                    section.data(52).dtTransOffset = 78;

                    ;% rtB.mkt3ad4pyq
                    section.data(53).logicalSrcIdx = 56;
                    section.data(53).dtTransOffset = 79;

                    ;% rtB.ehqzdwrgsf
                    section.data(54).logicalSrcIdx = 57;
                    section.data(54).dtTransOffset = 81;

                    ;% rtB.fmwoevyy1z
                    section.data(55).logicalSrcIdx = 58;
                    section.data(55).dtTransOffset = 83;

                    ;% rtB.imbxgfc4ak
                    section.data(56).logicalSrcIdx = 59;
                    section.data(56).dtTransOffset = 85;

                    ;% rtB.p4tlufthqw
                    section.data(57).logicalSrcIdx = 60;
                    section.data(57).dtTransOffset = 87;

                    ;% rtB.nkhwej22z3
                    section.data(58).logicalSrcIdx = 61;
                    section.data(58).dtTransOffset = 89;

                    ;% rtB.lcm31d2cuv
                    section.data(59).logicalSrcIdx = 62;
                    section.data(59).dtTransOffset = 91;

                    ;% rtB.jaxbhot51p
                    section.data(60).logicalSrcIdx = 63;
                    section.data(60).dtTransOffset = 93;

                    ;% rtB.owyelytkl4
                    section.data(61).logicalSrcIdx = 64;
                    section.data(61).dtTransOffset = 95;

                    ;% rtB.nz0veajr34
                    section.data(62).logicalSrcIdx = 65;
                    section.data(62).dtTransOffset = 96;

                    ;% rtB.l0fogrw55g
                    section.data(63).logicalSrcIdx = 66;
                    section.data(63).dtTransOffset = 97;

                    ;% rtB.ecwdayciz4
                    section.data(64).logicalSrcIdx = 67;
                    section.data(64).dtTransOffset = 99;

                    ;% rtB.b4m0uyma5n
                    section.data(65).logicalSrcIdx = 68;
                    section.data(65).dtTransOffset = 101;

                    ;% rtB.c3wmealgiz
                    section.data(66).logicalSrcIdx = 69;
                    section.data(66).dtTransOffset = 102;

            nTotData = nTotData + section.nData;
            sigMap.sections(2) = section;
            clear section

            section.nData     = 16;
            section.data(16)  = dumData; %prealloc

                    ;% rtB.j3xgfsagbd
                    section.data(1).logicalSrcIdx = 70;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.hbotkeaclm
                    section.data(2).logicalSrcIdx = 71;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.iiultfa0yi
                    section.data(3).logicalSrcIdx = 72;
                    section.data(3).dtTransOffset = 2;

                    ;% rtB.gbnlfgyum1
                    section.data(4).logicalSrcIdx = 73;
                    section.data(4).dtTransOffset = 3;

                    ;% rtB.kv1yw00kog
                    section.data(5).logicalSrcIdx = 74;
                    section.data(5).dtTransOffset = 4;

                    ;% rtB.fdnho0gvji
                    section.data(6).logicalSrcIdx = 75;
                    section.data(6).dtTransOffset = 5;

                    ;% rtB.oakl0w4pqn
                    section.data(7).logicalSrcIdx = 76;
                    section.data(7).dtTransOffset = 6;

                    ;% rtB.miy12mwpno
                    section.data(8).logicalSrcIdx = 77;
                    section.data(8).dtTransOffset = 7;

                    ;% rtB.earihymrhz
                    section.data(9).logicalSrcIdx = 78;
                    section.data(9).dtTransOffset = 8;

                    ;% rtB.jua5gapl55
                    section.data(10).logicalSrcIdx = 79;
                    section.data(10).dtTransOffset = 9;

                    ;% rtB.kzqruazo3h
                    section.data(11).logicalSrcIdx = 80;
                    section.data(11).dtTransOffset = 10;

                    ;% rtB.d5duzr3tcn
                    section.data(12).logicalSrcIdx = 81;
                    section.data(12).dtTransOffset = 11;

                    ;% rtB.fmf24kznuy
                    section.data(13).logicalSrcIdx = 82;
                    section.data(13).dtTransOffset = 12;

                    ;% rtB.luf4se5thf
                    section.data(14).logicalSrcIdx = 83;
                    section.data(14).dtTransOffset = 13;

                    ;% rtB.l4mszvm4ey
                    section.data(15).logicalSrcIdx = 84;
                    section.data(15).dtTransOffset = 14;

                    ;% rtB.ek3b525y33
                    section.data(16).logicalSrcIdx = 85;
                    section.data(16).dtTransOffset = 15;

            nTotData = nTotData + section.nData;
            sigMap.sections(3) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtB.onbve342oz.a2lfbsy4cs
                    section.data(1).logicalSrcIdx = 86;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.onbve342oz.ljmanj53r0
                    section.data(2).logicalSrcIdx = 87;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.onbve342oz.fjr3lpwqa5
                    section.data(3).logicalSrcIdx = 88;
                    section.data(3).dtTransOffset = 2;

                    ;% rtB.onbve342oz.c0bgxpqg0v
                    section.data(4).logicalSrcIdx = 89;
                    section.data(4).dtTransOffset = 3;

                    ;% rtB.onbve342oz.bi4luawlp4
                    section.data(5).logicalSrcIdx = 90;
                    section.data(5).dtTransOffset = 4;

                    ;% rtB.onbve342oz.m1qr1ecdnb
                    section.data(6).logicalSrcIdx = 91;
                    section.data(6).dtTransOffset = 5;

            nTotData = nTotData + section.nData;
            sigMap.sections(4) = section;
            clear section

            section.nData     = 3;
            section.data(3)  = dumData; %prealloc

                    ;% rtB.onbve342oz.jcnq3xzaim
                    section.data(1).logicalSrcIdx = 92;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.onbve342oz.o45o0wsteg
                    section.data(2).logicalSrcIdx = 93;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.onbve342oz.orstwbmzqt
                    section.data(3).logicalSrcIdx = 94;
                    section.data(3).dtTransOffset = 2;

            nTotData = nTotData + section.nData;
            sigMap.sections(5) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.onbve342oz.hdj3wqdohr.mivsv0p1ga
                    section.data(1).logicalSrcIdx = 95;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(6) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.onbve342oz.em1ujbr42u.di4cc0djtg
                    section.data(1).logicalSrcIdx = 96;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(7) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.onbve342oz.gg21spqnj5.kgfafranqp
                    section.data(1).logicalSrcIdx = 97;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(8) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtB.i4guox0dks.jm4yi4zlhr
                    section.data(1).logicalSrcIdx = 98;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.i4guox0dks.kv5myklx1w
                    section.data(2).logicalSrcIdx = 99;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.i4guox0dks.ovel3cjtov
                    section.data(3).logicalSrcIdx = 100;
                    section.data(3).dtTransOffset = 2;

                    ;% rtB.i4guox0dks.lftyf30dts
                    section.data(4).logicalSrcIdx = 101;
                    section.data(4).dtTransOffset = 3;

                    ;% rtB.i4guox0dks.akucnpziw4
                    section.data(5).logicalSrcIdx = 102;
                    section.data(5).dtTransOffset = 4;

                    ;% rtB.i4guox0dks.hsac3hu1nf
                    section.data(6).logicalSrcIdx = 103;
                    section.data(6).dtTransOffset = 5;

            nTotData = nTotData + section.nData;
            sigMap.sections(9) = section;
            clear section

            section.nData     = 3;
            section.data(3)  = dumData; %prealloc

                    ;% rtB.i4guox0dks.ayp0fkjftj
                    section.data(1).logicalSrcIdx = 104;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.i4guox0dks.ku2mk1f0wq
                    section.data(2).logicalSrcIdx = 105;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.i4guox0dks.jvwwoyxizw
                    section.data(3).logicalSrcIdx = 106;
                    section.data(3).dtTransOffset = 2;

            nTotData = nTotData + section.nData;
            sigMap.sections(10) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.i4guox0dks.ke0ovyvkjxg.mivsv0p1ga
                    section.data(1).logicalSrcIdx = 107;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(11) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.i4guox0dks.cg52ak5rbj5.di4cc0djtg
                    section.data(1).logicalSrcIdx = 108;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(12) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.i4guox0dks.bkqbq1qpitt.kgfafranqp
                    section.data(1).logicalSrcIdx = 109;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(13) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtB.awk1sqt1lf.a2lfbsy4cs
                    section.data(1).logicalSrcIdx = 110;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.awk1sqt1lf.ljmanj53r0
                    section.data(2).logicalSrcIdx = 111;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.awk1sqt1lf.fjr3lpwqa5
                    section.data(3).logicalSrcIdx = 112;
                    section.data(3).dtTransOffset = 2;

                    ;% rtB.awk1sqt1lf.c0bgxpqg0v
                    section.data(4).logicalSrcIdx = 113;
                    section.data(4).dtTransOffset = 3;

                    ;% rtB.awk1sqt1lf.bi4luawlp4
                    section.data(5).logicalSrcIdx = 114;
                    section.data(5).dtTransOffset = 4;

                    ;% rtB.awk1sqt1lf.m1qr1ecdnb
                    section.data(6).logicalSrcIdx = 115;
                    section.data(6).dtTransOffset = 5;

            nTotData = nTotData + section.nData;
            sigMap.sections(14) = section;
            clear section

            section.nData     = 3;
            section.data(3)  = dumData; %prealloc

                    ;% rtB.awk1sqt1lf.jcnq3xzaim
                    section.data(1).logicalSrcIdx = 116;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.awk1sqt1lf.o45o0wsteg
                    section.data(2).logicalSrcIdx = 117;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.awk1sqt1lf.orstwbmzqt
                    section.data(3).logicalSrcIdx = 118;
                    section.data(3).dtTransOffset = 2;

            nTotData = nTotData + section.nData;
            sigMap.sections(15) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.awk1sqt1lf.hdj3wqdohr.mivsv0p1ga
                    section.data(1).logicalSrcIdx = 119;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(16) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.awk1sqt1lf.em1ujbr42u.di4cc0djtg
                    section.data(1).logicalSrcIdx = 120;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(17) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.awk1sqt1lf.gg21spqnj5.kgfafranqp
                    section.data(1).logicalSrcIdx = 121;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(18) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtB.hquvqsfosa.jm4yi4zlhr
                    section.data(1).logicalSrcIdx = 122;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.hquvqsfosa.kv5myklx1w
                    section.data(2).logicalSrcIdx = 123;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.hquvqsfosa.ovel3cjtov
                    section.data(3).logicalSrcIdx = 124;
                    section.data(3).dtTransOffset = 2;

                    ;% rtB.hquvqsfosa.lftyf30dts
                    section.data(4).logicalSrcIdx = 125;
                    section.data(4).dtTransOffset = 3;

                    ;% rtB.hquvqsfosa.akucnpziw4
                    section.data(5).logicalSrcIdx = 126;
                    section.data(5).dtTransOffset = 4;

                    ;% rtB.hquvqsfosa.hsac3hu1nf
                    section.data(6).logicalSrcIdx = 127;
                    section.data(6).dtTransOffset = 5;

            nTotData = nTotData + section.nData;
            sigMap.sections(19) = section;
            clear section

            section.nData     = 3;
            section.data(3)  = dumData; %prealloc

                    ;% rtB.hquvqsfosa.ayp0fkjftj
                    section.data(1).logicalSrcIdx = 128;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.hquvqsfosa.ku2mk1f0wq
                    section.data(2).logicalSrcIdx = 129;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.hquvqsfosa.jvwwoyxizw
                    section.data(3).logicalSrcIdx = 130;
                    section.data(3).dtTransOffset = 2;

            nTotData = nTotData + section.nData;
            sigMap.sections(20) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.hquvqsfosa.ke0ovyvkjxg.mivsv0p1ga
                    section.data(1).logicalSrcIdx = 131;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(21) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.hquvqsfosa.cg52ak5rbj5.di4cc0djtg
                    section.data(1).logicalSrcIdx = 132;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(22) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.hquvqsfosa.bkqbq1qpitt.kgfafranqp
                    section.data(1).logicalSrcIdx = 133;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(23) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtB.hm4diydndl.a2lfbsy4cs
                    section.data(1).logicalSrcIdx = 134;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.hm4diydndl.ljmanj53r0
                    section.data(2).logicalSrcIdx = 135;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.hm4diydndl.fjr3lpwqa5
                    section.data(3).logicalSrcIdx = 136;
                    section.data(3).dtTransOffset = 2;

                    ;% rtB.hm4diydndl.c0bgxpqg0v
                    section.data(4).logicalSrcIdx = 137;
                    section.data(4).dtTransOffset = 3;

                    ;% rtB.hm4diydndl.bi4luawlp4
                    section.data(5).logicalSrcIdx = 138;
                    section.data(5).dtTransOffset = 4;

                    ;% rtB.hm4diydndl.m1qr1ecdnb
                    section.data(6).logicalSrcIdx = 139;
                    section.data(6).dtTransOffset = 5;

            nTotData = nTotData + section.nData;
            sigMap.sections(24) = section;
            clear section

            section.nData     = 3;
            section.data(3)  = dumData; %prealloc

                    ;% rtB.hm4diydndl.jcnq3xzaim
                    section.data(1).logicalSrcIdx = 140;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.hm4diydndl.o45o0wsteg
                    section.data(2).logicalSrcIdx = 141;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.hm4diydndl.orstwbmzqt
                    section.data(3).logicalSrcIdx = 142;
                    section.data(3).dtTransOffset = 2;

            nTotData = nTotData + section.nData;
            sigMap.sections(25) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.hm4diydndl.hdj3wqdohr.mivsv0p1ga
                    section.data(1).logicalSrcIdx = 143;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(26) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.hm4diydndl.em1ujbr42u.di4cc0djtg
                    section.data(1).logicalSrcIdx = 144;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(27) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.hm4diydndl.gg21spqnj5.kgfafranqp
                    section.data(1).logicalSrcIdx = 145;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(28) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtB.do3rpmepfq.jm4yi4zlhr
                    section.data(1).logicalSrcIdx = 146;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.do3rpmepfq.kv5myklx1w
                    section.data(2).logicalSrcIdx = 147;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.do3rpmepfq.ovel3cjtov
                    section.data(3).logicalSrcIdx = 148;
                    section.data(3).dtTransOffset = 2;

                    ;% rtB.do3rpmepfq.lftyf30dts
                    section.data(4).logicalSrcIdx = 149;
                    section.data(4).dtTransOffset = 3;

                    ;% rtB.do3rpmepfq.akucnpziw4
                    section.data(5).logicalSrcIdx = 150;
                    section.data(5).dtTransOffset = 4;

                    ;% rtB.do3rpmepfq.hsac3hu1nf
                    section.data(6).logicalSrcIdx = 151;
                    section.data(6).dtTransOffset = 5;

            nTotData = nTotData + section.nData;
            sigMap.sections(29) = section;
            clear section

            section.nData     = 3;
            section.data(3)  = dumData; %prealloc

                    ;% rtB.do3rpmepfq.ayp0fkjftj
                    section.data(1).logicalSrcIdx = 152;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.do3rpmepfq.ku2mk1f0wq
                    section.data(2).logicalSrcIdx = 153;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.do3rpmepfq.jvwwoyxizw
                    section.data(3).logicalSrcIdx = 154;
                    section.data(3).dtTransOffset = 2;

            nTotData = nTotData + section.nData;
            sigMap.sections(30) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.do3rpmepfq.ke0ovyvkjxg.mivsv0p1ga
                    section.data(1).logicalSrcIdx = 155;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(31) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.do3rpmepfq.cg52ak5rbj5.di4cc0djtg
                    section.data(1).logicalSrcIdx = 156;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(32) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.do3rpmepfq.bkqbq1qpitt.kgfafranqp
                    section.data(1).logicalSrcIdx = 157;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(33) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtB.loki5osupmm.a2lfbsy4cs
                    section.data(1).logicalSrcIdx = 158;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.loki5osupmm.ljmanj53r0
                    section.data(2).logicalSrcIdx = 159;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.loki5osupmm.fjr3lpwqa5
                    section.data(3).logicalSrcIdx = 160;
                    section.data(3).dtTransOffset = 2;

                    ;% rtB.loki5osupmm.c0bgxpqg0v
                    section.data(4).logicalSrcIdx = 161;
                    section.data(4).dtTransOffset = 3;

                    ;% rtB.loki5osupmm.bi4luawlp4
                    section.data(5).logicalSrcIdx = 162;
                    section.data(5).dtTransOffset = 4;

                    ;% rtB.loki5osupmm.m1qr1ecdnb
                    section.data(6).logicalSrcIdx = 163;
                    section.data(6).dtTransOffset = 5;

            nTotData = nTotData + section.nData;
            sigMap.sections(34) = section;
            clear section

            section.nData     = 3;
            section.data(3)  = dumData; %prealloc

                    ;% rtB.loki5osupmm.jcnq3xzaim
                    section.data(1).logicalSrcIdx = 164;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.loki5osupmm.o45o0wsteg
                    section.data(2).logicalSrcIdx = 165;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.loki5osupmm.orstwbmzqt
                    section.data(3).logicalSrcIdx = 166;
                    section.data(3).dtTransOffset = 2;

            nTotData = nTotData + section.nData;
            sigMap.sections(35) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.loki5osupmm.hdj3wqdohr.mivsv0p1ga
                    section.data(1).logicalSrcIdx = 167;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(36) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.loki5osupmm.em1ujbr42u.di4cc0djtg
                    section.data(1).logicalSrcIdx = 168;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(37) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.loki5osupmm.gg21spqnj5.kgfafranqp
                    section.data(1).logicalSrcIdx = 169;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(38) = section;
            clear section

            section.nData     = 6;
            section.data(6)  = dumData; %prealloc

                    ;% rtB.nvd5ofuthxp.jm4yi4zlhr
                    section.data(1).logicalSrcIdx = 170;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.nvd5ofuthxp.kv5myklx1w
                    section.data(2).logicalSrcIdx = 171;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.nvd5ofuthxp.ovel3cjtov
                    section.data(3).logicalSrcIdx = 172;
                    section.data(3).dtTransOffset = 2;

                    ;% rtB.nvd5ofuthxp.lftyf30dts
                    section.data(4).logicalSrcIdx = 173;
                    section.data(4).dtTransOffset = 3;

                    ;% rtB.nvd5ofuthxp.akucnpziw4
                    section.data(5).logicalSrcIdx = 174;
                    section.data(5).dtTransOffset = 4;

                    ;% rtB.nvd5ofuthxp.hsac3hu1nf
                    section.data(6).logicalSrcIdx = 175;
                    section.data(6).dtTransOffset = 5;

            nTotData = nTotData + section.nData;
            sigMap.sections(39) = section;
            clear section

            section.nData     = 3;
            section.data(3)  = dumData; %prealloc

                    ;% rtB.nvd5ofuthxp.ayp0fkjftj
                    section.data(1).logicalSrcIdx = 176;
                    section.data(1).dtTransOffset = 0;

                    ;% rtB.nvd5ofuthxp.ku2mk1f0wq
                    section.data(2).logicalSrcIdx = 177;
                    section.data(2).dtTransOffset = 1;

                    ;% rtB.nvd5ofuthxp.jvwwoyxizw
                    section.data(3).logicalSrcIdx = 178;
                    section.data(3).dtTransOffset = 2;

            nTotData = nTotData + section.nData;
            sigMap.sections(40) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.nvd5ofuthxp.ke0ovyvkjxg.mivsv0p1ga
                    section.data(1).logicalSrcIdx = 179;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(41) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.nvd5ofuthxp.cg52ak5rbj5.di4cc0djtg
                    section.data(1).logicalSrcIdx = 180;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(42) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtB.nvd5ofuthxp.bkqbq1qpitt.kgfafranqp
                    section.data(1).logicalSrcIdx = 181;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            sigMap.sections(43) = section;
            clear section


            ;%
            ;% Non-auto Data (signal)
            ;%


        ;%
        ;% Add final counts to struct.
        ;%
        sigMap.nTotData = nTotData;



    ;%*******************
    ;% Create DWork Map *
    ;%*******************
    
        nTotData      = 0; %add to this count as we go
        nTotSects     = 52;
        sectIdxOffset = 43;

        ;%
        ;% Define dummy sections & preallocate arrays
        ;%
        dumSection.nData = -1;
        dumSection.data  = [];

        dumData.logicalSrcIdx = -1;
        dumData.dtTransOffset = -1;

        ;%
        ;% Init/prealloc dworkMap
        ;%
        dworkMap.nSections           = nTotSects;
        dworkMap.sectIdxOffset       = sectIdxOffset;
            dworkMap.sections(nTotSects) = dumSection; %prealloc
        dworkMap.nTotData            = -1;

        ;%
        ;% Auto data (rtDW)
        ;%
            section.nData     = 7;
            section.data(7)  = dumData; %prealloc

                    ;% rtDW.o0sdw4ga04
                    section.data(1).logicalSrcIdx = 0;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.dqzphpqe0m
                    section.data(2).logicalSrcIdx = 1;
                    section.data(2).dtTransOffset = 3;

                    ;% rtDW.gvn4ktrc32.modelTStart
                    section.data(3).logicalSrcIdx = 2;
                    section.data(3).dtTransOffset = 4;

                    ;% rtDW.cllnfwz3tb.modelTStart
                    section.data(4).logicalSrcIdx = 3;
                    section.data(4).dtTransOffset = 5;

                    ;% rtDW.mfjk4saosj.modelTStart
                    section.data(5).logicalSrcIdx = 4;
                    section.data(5).dtTransOffset = 6;

                    ;% rtDW.lvbigskvem.modelTStart
                    section.data(6).logicalSrcIdx = 5;
                    section.data(6).dtTransOffset = 7;

                    ;% rtDW.lz3migfs5x.modelTStart
                    section.data(7).logicalSrcIdx = 6;
                    section.data(7).dtTransOffset = 8;

            nTotData = nTotData + section.nData;
            dworkMap.sections(1) = section;
            clear section

            section.nData     = 28;
            section.data(28)  = dumData; %prealloc

                    ;% rtDW.jerqxxmqcs.AS
                    section.data(1).logicalSrcIdx = 7;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.lesysrk11a.LoggedData
                    section.data(2).logicalSrcIdx = 8;
                    section.data(2).dtTransOffset = 1;

                    ;% rtDW.ebpteyuskx.LoggedData
                    section.data(3).logicalSrcIdx = 9;
                    section.data(3).dtTransOffset = 2;

                    ;% rtDW.aa0w4souqn.LoggedData
                    section.data(4).logicalSrcIdx = 10;
                    section.data(4).dtTransOffset = 3;

                    ;% rtDW.a4g4qpnema.LoggedData
                    section.data(5).logicalSrcIdx = 11;
                    section.data(5).dtTransOffset = 6;

                    ;% rtDW.ijxmenl5q5.LoggedData
                    section.data(6).logicalSrcIdx = 12;
                    section.data(6).dtTransOffset = 7;

                    ;% rtDW.iw0piyjyup.LoggedData
                    section.data(7).logicalSrcIdx = 13;
                    section.data(7).dtTransOffset = 9;

                    ;% rtDW.lxd2jdhomv.LoggedData
                    section.data(8).logicalSrcIdx = 14;
                    section.data(8).dtTransOffset = 11;

                    ;% rtDW.ov555evyfn.LoggedData
                    section.data(9).logicalSrcIdx = 15;
                    section.data(9).dtTransOffset = 13;

                    ;% rtDW.mmnltffxgf.TUbufferPtrs
                    section.data(10).logicalSrcIdx = 16;
                    section.data(10).dtTransOffset = 15;

                    ;% rtDW.d12kd2d2y2.TUbufferPtrs
                    section.data(11).logicalSrcIdx = 17;
                    section.data(11).dtTransOffset = 19;

                    ;% rtDW.mp4ukcqxxq.LoggedData
                    section.data(12).logicalSrcIdx = 18;
                    section.data(12).dtTransOffset = 23;

                    ;% rtDW.oabkbijn5b.LoggedData
                    section.data(13).logicalSrcIdx = 19;
                    section.data(13).dtTransOffset = 24;

                    ;% rtDW.cpr30yglxz.LoggedData
                    section.data(14).logicalSrcIdx = 20;
                    section.data(14).dtTransOffset = 26;

                    ;% rtDW.abvlyepici.LoggedData
                    section.data(15).logicalSrcIdx = 21;
                    section.data(15).dtTransOffset = 28;

                    ;% rtDW.pltfns05y4.AQHandles
                    section.data(16).logicalSrcIdx = 22;
                    section.data(16).dtTransOffset = 29;

                    ;% rtDW.ocdwnwqnp5.AQHandles
                    section.data(17).logicalSrcIdx = 23;
                    section.data(17).dtTransOffset = 30;

                    ;% rtDW.munpszj1ln.AQHandles
                    section.data(18).logicalSrcIdx = 24;
                    section.data(18).dtTransOffset = 31;

                    ;% rtDW.dzbb1jxxpe.AQHandles
                    section.data(19).logicalSrcIdx = 25;
                    section.data(19).dtTransOffset = 32;

                    ;% rtDW.phmvx4tgje.TUbufferPtrs
                    section.data(20).logicalSrcIdx = 26;
                    section.data(20).dtTransOffset = 33;

                    ;% rtDW.nut5kfpzra.LoggedData
                    section.data(21).logicalSrcIdx = 27;
                    section.data(21).dtTransOffset = 35;

                    ;% rtDW.j21xxsftse.LoggedData
                    section.data(22).logicalSrcIdx = 28;
                    section.data(22).dtTransOffset = 36;

                    ;% rtDW.bjikh0xvea.TUbufferPtrs
                    section.data(23).logicalSrcIdx = 29;
                    section.data(23).dtTransOffset = 37;

                    ;% rtDW.mpqxasqd4p.TUbufferPtrs
                    section.data(24).logicalSrcIdx = 30;
                    section.data(24).dtTransOffset = 41;

                    ;% rtDW.ksfkcfldsa.LoggedData
                    section.data(25).logicalSrcIdx = 31;
                    section.data(25).dtTransOffset = 45;

                    ;% rtDW.bfjshdunpe.AQHandles
                    section.data(26).logicalSrcIdx = 32;
                    section.data(26).dtTransOffset = 46;

                    ;% rtDW.o0mgvc0war.AQHandles
                    section.data(27).logicalSrcIdx = 33;
                    section.data(27).dtTransOffset = 47;

                    ;% rtDW.gzhxp04pko.LoggedData
                    section.data(28).logicalSrcIdx = 34;
                    section.data(28).dtTransOffset = 48;

            nTotData = nTotData + section.nData;
            dworkMap.sections(2) = section;
            clear section

            section.nData     = 15;
            section.data(15)  = dumData; %prealloc

                    ;% rtDW.mrbodwon5t
                    section.data(1).logicalSrcIdx = 35;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.gpyrwaevh4.Tail
                    section.data(2).logicalSrcIdx = 36;
                    section.data(2).dtTransOffset = 11;

                    ;% rtDW.ctgjr0hgl4.Tail
                    section.data(3).logicalSrcIdx = 37;
                    section.data(3).dtTransOffset = 20;

                    ;% rtDW.hitcyyh2cc.Tail
                    section.data(4).logicalSrcIdx = 38;
                    section.data(4).dtTransOffset = 29;

                    ;% rtDW.pux4o24isy.Tail
                    section.data(5).logicalSrcIdx = 39;
                    section.data(5).dtTransOffset = 30;

                    ;% rtDW.omh2qyy13y.Tail
                    section.data(6).logicalSrcIdx = 40;
                    section.data(6).dtTransOffset = 39;

                    ;% rtDW.lnmpbjbdw2
                    section.data(7).logicalSrcIdx = 41;
                    section.data(7).dtTransOffset = 48;

                    ;% rtDW.evno5delc3
                    section.data(8).logicalSrcIdx = 42;
                    section.data(8).dtTransOffset = 49;

                    ;% rtDW.cfqgqowmvq
                    section.data(9).logicalSrcIdx = 43;
                    section.data(9).dtTransOffset = 50;

                    ;% rtDW.fdovdthfvs
                    section.data(10).logicalSrcIdx = 44;
                    section.data(10).dtTransOffset = 51;

                    ;% rtDW.incnco1a1f
                    section.data(11).logicalSrcIdx = 45;
                    section.data(11).dtTransOffset = 52;

                    ;% rtDW.mgkjzknwtu
                    section.data(12).logicalSrcIdx = 46;
                    section.data(12).dtTransOffset = 53;

                    ;% rtDW.hqkbnj2vyw
                    section.data(13).logicalSrcIdx = 47;
                    section.data(13).dtTransOffset = 54;

                    ;% rtDW.l3nrx2fusi
                    section.data(14).logicalSrcIdx = 48;
                    section.data(14).dtTransOffset = 55;

                    ;% rtDW.cfecjurfjc
                    section.data(15).logicalSrcIdx = 49;
                    section.data(15).dtTransOffset = 56;

            nTotData = nTotData + section.nData;
            dworkMap.sections(3) = section;
            clear section

            section.nData     = 2;
            section.data(2)  = dumData; %prealloc

                    ;% rtDW.gcqjhvst4s
                    section.data(1).logicalSrcIdx = 50;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.hhs04u0so5
                    section.data(2).logicalSrcIdx = 51;
                    section.data(2).dtTransOffset = 1;

            nTotData = nTotData + section.nData;
            dworkMap.sections(4) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.onbve342oz.kc0czxlvix
                    section.data(1).logicalSrcIdx = 52;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(5) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.onbve342oz.o533iywxmw
                    section.data(1).logicalSrcIdx = 53;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(6) = section;
            clear section

            section.nData     = 4;
            section.data(4)  = dumData; %prealloc

                    ;% rtDW.onbve342oz.gcdjak4xrh
                    section.data(1).logicalSrcIdx = 54;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.onbve342oz.idx1opyf2w
                    section.data(2).logicalSrcIdx = 55;
                    section.data(2).dtTransOffset = 1;

                    ;% rtDW.onbve342oz.eduysmhfye
                    section.data(3).logicalSrcIdx = 56;
                    section.data(3).dtTransOffset = 2;

                    ;% rtDW.onbve342oz.ka3uhwvx5i
                    section.data(4).logicalSrcIdx = 57;
                    section.data(4).dtTransOffset = 3;

            nTotData = nTotData + section.nData;
            dworkMap.sections(7) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.onbve342oz.hdj3wqdohr.nbq3ifmreh
                    section.data(1).logicalSrcIdx = 58;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(8) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.onbve342oz.em1ujbr42u.bl5unxe5qb
                    section.data(1).logicalSrcIdx = 59;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(9) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.onbve342oz.gg21spqnj5.fgqiszwjfb
                    section.data(1).logicalSrcIdx = 60;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(10) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.i4guox0dks.hv3r2ijr2x
                    section.data(1).logicalSrcIdx = 61;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(11) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.i4guox0dks.hrt2icxcxe
                    section.data(1).logicalSrcIdx = 62;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(12) = section;
            clear section

            section.nData     = 4;
            section.data(4)  = dumData; %prealloc

                    ;% rtDW.i4guox0dks.kt00ipvbzb
                    section.data(1).logicalSrcIdx = 63;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.i4guox0dks.hp013rjhzw
                    section.data(2).logicalSrcIdx = 64;
                    section.data(2).dtTransOffset = 1;

                    ;% rtDW.i4guox0dks.blpvwhdvr0
                    section.data(3).logicalSrcIdx = 65;
                    section.data(3).dtTransOffset = 2;

                    ;% rtDW.i4guox0dks.pzz3djh1m0
                    section.data(4).logicalSrcIdx = 66;
                    section.data(4).dtTransOffset = 3;

            nTotData = nTotData + section.nData;
            dworkMap.sections(13) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.i4guox0dks.ke0ovyvkjxg.nbq3ifmreh
                    section.data(1).logicalSrcIdx = 67;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(14) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.i4guox0dks.cg52ak5rbj5.bl5unxe5qb
                    section.data(1).logicalSrcIdx = 68;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(15) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.i4guox0dks.bkqbq1qpitt.fgqiszwjfb
                    section.data(1).logicalSrcIdx = 69;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(16) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.awk1sqt1lf.kc0czxlvix
                    section.data(1).logicalSrcIdx = 70;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(17) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.awk1sqt1lf.o533iywxmw
                    section.data(1).logicalSrcIdx = 71;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(18) = section;
            clear section

            section.nData     = 4;
            section.data(4)  = dumData; %prealloc

                    ;% rtDW.awk1sqt1lf.gcdjak4xrh
                    section.data(1).logicalSrcIdx = 72;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.awk1sqt1lf.idx1opyf2w
                    section.data(2).logicalSrcIdx = 73;
                    section.data(2).dtTransOffset = 1;

                    ;% rtDW.awk1sqt1lf.eduysmhfye
                    section.data(3).logicalSrcIdx = 74;
                    section.data(3).dtTransOffset = 2;

                    ;% rtDW.awk1sqt1lf.ka3uhwvx5i
                    section.data(4).logicalSrcIdx = 75;
                    section.data(4).dtTransOffset = 3;

            nTotData = nTotData + section.nData;
            dworkMap.sections(19) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.awk1sqt1lf.hdj3wqdohr.nbq3ifmreh
                    section.data(1).logicalSrcIdx = 76;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(20) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.awk1sqt1lf.em1ujbr42u.bl5unxe5qb
                    section.data(1).logicalSrcIdx = 77;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(21) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.awk1sqt1lf.gg21spqnj5.fgqiszwjfb
                    section.data(1).logicalSrcIdx = 78;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(22) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.hquvqsfosa.hv3r2ijr2x
                    section.data(1).logicalSrcIdx = 79;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(23) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.hquvqsfosa.hrt2icxcxe
                    section.data(1).logicalSrcIdx = 80;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(24) = section;
            clear section

            section.nData     = 4;
            section.data(4)  = dumData; %prealloc

                    ;% rtDW.hquvqsfosa.kt00ipvbzb
                    section.data(1).logicalSrcIdx = 81;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.hquvqsfosa.hp013rjhzw
                    section.data(2).logicalSrcIdx = 82;
                    section.data(2).dtTransOffset = 1;

                    ;% rtDW.hquvqsfosa.blpvwhdvr0
                    section.data(3).logicalSrcIdx = 83;
                    section.data(3).dtTransOffset = 2;

                    ;% rtDW.hquvqsfosa.pzz3djh1m0
                    section.data(4).logicalSrcIdx = 84;
                    section.data(4).dtTransOffset = 3;

            nTotData = nTotData + section.nData;
            dworkMap.sections(25) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.hquvqsfosa.ke0ovyvkjxg.nbq3ifmreh
                    section.data(1).logicalSrcIdx = 85;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(26) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.hquvqsfosa.cg52ak5rbj5.bl5unxe5qb
                    section.data(1).logicalSrcIdx = 86;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(27) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.hquvqsfosa.bkqbq1qpitt.fgqiszwjfb
                    section.data(1).logicalSrcIdx = 87;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(28) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.hm4diydndl.kc0czxlvix
                    section.data(1).logicalSrcIdx = 88;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(29) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.hm4diydndl.o533iywxmw
                    section.data(1).logicalSrcIdx = 89;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(30) = section;
            clear section

            section.nData     = 4;
            section.data(4)  = dumData; %prealloc

                    ;% rtDW.hm4diydndl.gcdjak4xrh
                    section.data(1).logicalSrcIdx = 90;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.hm4diydndl.idx1opyf2w
                    section.data(2).logicalSrcIdx = 91;
                    section.data(2).dtTransOffset = 1;

                    ;% rtDW.hm4diydndl.eduysmhfye
                    section.data(3).logicalSrcIdx = 92;
                    section.data(3).dtTransOffset = 2;

                    ;% rtDW.hm4diydndl.ka3uhwvx5i
                    section.data(4).logicalSrcIdx = 93;
                    section.data(4).dtTransOffset = 3;

            nTotData = nTotData + section.nData;
            dworkMap.sections(31) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.hm4diydndl.hdj3wqdohr.nbq3ifmreh
                    section.data(1).logicalSrcIdx = 94;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(32) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.hm4diydndl.em1ujbr42u.bl5unxe5qb
                    section.data(1).logicalSrcIdx = 95;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(33) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.hm4diydndl.gg21spqnj5.fgqiszwjfb
                    section.data(1).logicalSrcIdx = 96;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(34) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.do3rpmepfq.hv3r2ijr2x
                    section.data(1).logicalSrcIdx = 97;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(35) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.do3rpmepfq.hrt2icxcxe
                    section.data(1).logicalSrcIdx = 98;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(36) = section;
            clear section

            section.nData     = 4;
            section.data(4)  = dumData; %prealloc

                    ;% rtDW.do3rpmepfq.kt00ipvbzb
                    section.data(1).logicalSrcIdx = 99;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.do3rpmepfq.hp013rjhzw
                    section.data(2).logicalSrcIdx = 100;
                    section.data(2).dtTransOffset = 1;

                    ;% rtDW.do3rpmepfq.blpvwhdvr0
                    section.data(3).logicalSrcIdx = 101;
                    section.data(3).dtTransOffset = 2;

                    ;% rtDW.do3rpmepfq.pzz3djh1m0
                    section.data(4).logicalSrcIdx = 102;
                    section.data(4).dtTransOffset = 3;

            nTotData = nTotData + section.nData;
            dworkMap.sections(37) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.do3rpmepfq.ke0ovyvkjxg.nbq3ifmreh
                    section.data(1).logicalSrcIdx = 103;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(38) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.do3rpmepfq.cg52ak5rbj5.bl5unxe5qb
                    section.data(1).logicalSrcIdx = 104;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(39) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.do3rpmepfq.bkqbq1qpitt.fgqiszwjfb
                    section.data(1).logicalSrcIdx = 105;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(40) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.loki5osupmm.kc0czxlvix
                    section.data(1).logicalSrcIdx = 106;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(41) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.loki5osupmm.o533iywxmw
                    section.data(1).logicalSrcIdx = 107;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(42) = section;
            clear section

            section.nData     = 4;
            section.data(4)  = dumData; %prealloc

                    ;% rtDW.loki5osupmm.gcdjak4xrh
                    section.data(1).logicalSrcIdx = 108;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.loki5osupmm.idx1opyf2w
                    section.data(2).logicalSrcIdx = 109;
                    section.data(2).dtTransOffset = 1;

                    ;% rtDW.loki5osupmm.eduysmhfye
                    section.data(3).logicalSrcIdx = 110;
                    section.data(3).dtTransOffset = 2;

                    ;% rtDW.loki5osupmm.ka3uhwvx5i
                    section.data(4).logicalSrcIdx = 111;
                    section.data(4).dtTransOffset = 3;

            nTotData = nTotData + section.nData;
            dworkMap.sections(43) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.loki5osupmm.hdj3wqdohr.nbq3ifmreh
                    section.data(1).logicalSrcIdx = 112;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(44) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.loki5osupmm.em1ujbr42u.bl5unxe5qb
                    section.data(1).logicalSrcIdx = 113;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(45) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.loki5osupmm.gg21spqnj5.fgqiszwjfb
                    section.data(1).logicalSrcIdx = 114;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(46) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.nvd5ofuthxp.hv3r2ijr2x
                    section.data(1).logicalSrcIdx = 115;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(47) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.nvd5ofuthxp.hrt2icxcxe
                    section.data(1).logicalSrcIdx = 116;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(48) = section;
            clear section

            section.nData     = 4;
            section.data(4)  = dumData; %prealloc

                    ;% rtDW.nvd5ofuthxp.kt00ipvbzb
                    section.data(1).logicalSrcIdx = 117;
                    section.data(1).dtTransOffset = 0;

                    ;% rtDW.nvd5ofuthxp.hp013rjhzw
                    section.data(2).logicalSrcIdx = 118;
                    section.data(2).dtTransOffset = 1;

                    ;% rtDW.nvd5ofuthxp.blpvwhdvr0
                    section.data(3).logicalSrcIdx = 119;
                    section.data(3).dtTransOffset = 2;

                    ;% rtDW.nvd5ofuthxp.pzz3djh1m0
                    section.data(4).logicalSrcIdx = 120;
                    section.data(4).dtTransOffset = 3;

            nTotData = nTotData + section.nData;
            dworkMap.sections(49) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.nvd5ofuthxp.ke0ovyvkjxg.nbq3ifmreh
                    section.data(1).logicalSrcIdx = 121;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(50) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.nvd5ofuthxp.cg52ak5rbj5.bl5unxe5qb
                    section.data(1).logicalSrcIdx = 122;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(51) = section;
            clear section

            section.nData     = 1;
            section.data(1)  = dumData; %prealloc

                    ;% rtDW.nvd5ofuthxp.bkqbq1qpitt.fgqiszwjfb
                    section.data(1).logicalSrcIdx = 123;
                    section.data(1).dtTransOffset = 0;

            nTotData = nTotData + section.nData;
            dworkMap.sections(52) = section;
            clear section


            ;%
            ;% Non-auto Data (dwork)
            ;%


        ;%
        ;% Add final counts to struct.
        ;%
        dworkMap.nTotData = nTotData;



    ;%
    ;% Add individual maps to base struct.
    ;%

    targMap.paramMap  = paramMap;
    targMap.signalMap = sigMap;
    targMap.dworkMap  = dworkMap;

    ;%
    ;% Add checksums to base struct.
    ;%


    targMap.checksum0 = 1434004801;
    targMap.checksum1 = 1868107466;
    targMap.checksum2 = 4115688341;
    targMap.checksum3 = 1977790435;

