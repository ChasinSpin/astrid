// Print in Black ASA, 25% fill, support, brim, liquid glue, smooth/HT plate
// Part 5 has a 2 a green ASA ring that needs to be filled
// Part 6 needs support and Part 7 should be in TPU 5% fill

partNum                         = 0;        // 0 = All, 1 = Adapter1, 2 = Adapter2, 3 = Adapter3, 4 = Adapter3 Assembled, 5 = Adapter3 Cover, 6 = AdjustmentRings, 7 = AdjustmentRingsGromit

manifoldCorrection              = 0.01;
manifoldCorrection2             = manifoldCorrection * 2;

inch2Diameter                   = 50.69;
cameraDiameter                  = 35.4;
adapter1FlangeThickness         = 2.0;
adapter1Height                  = 38.0 + adapter1FlangeThickness;
adapter1FlangeDiameter          = 58.0;

adapter2Height                  = 38.0;
adapter2CollarDiameter          = 49.0;
adapter2CollarHeight            = 12.0;
adapter2CollarZOffset           = 2.0;
adapter2CollarBevelHeight       = 2.0;

adapter3PCBOffsetZ              = 60;       // Change this ONLY to change height of adapter
adapter3FlangeThickness         = 3.0;
adapter3PCBDimensions           = [39.5, 39.5, 1.65];
adapter3Height                  = adapter3PCBOffsetZ + adapter3PCBDimensions[2] + 12 + adapter3FlangeThickness;
adapter3FlangeDiameter          = 62.0;
adapter3RetentionHeight         = adapter3Height - 4.0;
adapter3RetentionWidth          = 6.0;
adapter3RetentionDepth          = 1.2;
adapter3InnerDiameter           = 41.6;
adapter3PCBPostHolesDistance    = 34.0;
adapter3PCBPostDiameter         = 2.5;
adapter3BoltHeadDiameter        = 4.2 + 0.3;
adapter3BoltHeadHeight          = 1.6;
adapter3BoltDiameter            = 2.45 + 0.4;
adapter3BoltThreadDiameter      = 2.35;
adapter3BoltTopHeight           = 3.0;
adapter3BoltThreadDepth         = (14.0 - (adapter3BoltTopHeight + adapter3PCBDimensions[2])) + 2.0;
adapter3PCBClearanceDimensions  = [inch2Diameter + manifoldCorrection2, 13.0, 8.0];
adapter3LensFlangeThickness     = 3.0;
adapter3LensFlangeInnerDiameter = 35.5;
adapter3TopPlateBoltRecessDia1  = 4.5;
adapter3TopBoltRadius           = adapter3FlangeDiameter/2 - 3.0;
adapter3CableClearanceBlock     = [22, 6, 15];

highlightRingOuterDiameter      = adapter3FlangeDiameter - 12.0;
highlightRingInnerDiameter      = highlightRingOuterDiameter - 5.0;
highlightRingThickness          = 0.8;

fanVentHoleDiameter             = 1.2;
fanVentDiameter                 = 40.0;

insertHoleDiameter              = 3.2 + 0.2;
insertHoleDepth                 = 5.0;
adapter3CoverDepth              = 7.0;

cableWidth                          = 17.0;
cableThickness                      = 3.0;
flexThickness                       = 0.7;  // The overall thickness of the tube as it ships (both sides)
flexCollarSurroundThickness         = 1.0;
flexCollarDepth                     = 6.0;
flexOuterLength                     = cableWidth + flexCollarSurroundThickness * 2;
flexOuterWidth1                     = cableThickness + flexCollarSurroundThickness * 2;
flexOuterWidth2                     = flexOuterWidth1 - 1.0;
flexOuterClampWidth1                = flexOuterWidth1 + flexThickness;
flexOuterClampWidth2                 = flexOuterWidth2 + flexThickness;
pcbConnectorHeight                  = 3.4;
pcbDimensions                       = [39.1, 39.1, 1.60];
caseMiddleHeight                    = pcbDimensions[2] + pcbConnectorHeight + cableWidth + 0.5;

collarVoidOffsetZ                   = 12.0;

flexOuterClampOuterBorder           = 1.5;
flexOuterClampInnerLength           = flexOuterLength + flexThickness;
flexOuterClampOuterWidth            = flexOuterClampWidth1 + flexOuterClampOuterBorder;
flexOuterClampOuterLength           = flexOuterLength + flexThickness + flexOuterClampOuterBorder;

flexCollarVoidLength                = flexOuterClampOuterLength + 1.8;
flexCollarVoidWidth                 = flexOuterClampOuterWidth + 0.5;
flexCollarVoidThickness             = flexCollarDepth + 0.75;
caseThickness                       = 1.2;
caseInnerDiameter                   = 56.57;
caseOuterDiameter                   = caseInnerDiameter + caseThickness*2;
flexCollarBlockDimensions           = [10.7, flexCollarVoidThickness + 1.75, 22];
flexCollarBlockOffsetY              = -1.0;

adjustmentRingInnerDiameter         = 51.0;
adjustmentRingOuterDiameter         = adjustmentRingInnerDiameter + 5.0;
adjustmentRingGromitHeight          = 3.0;
adjustmentRingGromitVoidHeight      = adjustmentRingGromitHeight + 0.3;
adjustmentRingGromitVoidDiameter    = adjustmentRingInnerDiameter + 2.0;
adjustmentRingGromitOffsetZ         = 2.0;
adjustmentRingGromitInnerDiameter   = 50.6;    



$fn                             = 80;



//if ( partNum == 0 || partNum == 1 ) adapter1();
//if ( partNum == 0 || partNum == 2 )
//    translate( [70, 0, 0] )
//        adapter2();
if ( partNum == 0 || partNum == 3 )
{
    translate( [140, 0, 0] )
        translate( [0, 0, adapter3Height] )
            rotate( [180, 0, 0] )
                adapter3Top();
    translate( [210, 0, 0] )
            adapter3Bottom();
}
if ( partNum == 4 )
    translate( [210, 0, 0] )
    {
        adapter3();
        translate( [0, 0, -adapter3CoverDepth] )
            adapter3Cover();
    }
        
if ( partNum == 5 )
    translate( [0, 0, 0] )
    {
        adapter3Cover();
    }
    
if ( partNum == 6 )
    translate( [0, 0, 0] )
    {
        adjustmentRings();
    }
    
    
if ( partNum == 7 )
    translate( [0, 0, 0] )
    {
        adjustmentRingGromit();
    }
    
    
   
    
module adjustmentRingGromit()
{
    donut(adjustmentRingGromitVoidDiameter, adjustmentRingGromitInnerDiameter, adjustmentRingGromitHeight);
}
 
 
    
module adjustmentRings()
{
    adjustmentRing(40.0);
    translate( [adjustmentRingOuterDiameter + 20, 0, 0] )
        adjustmentRing(20.0);
    translate( [(adjustmentRingOuterDiameter + 20)*2, 0, 0] )
        adjustmentRing(10.0);
}



module adjustmentRing(height)
{
    difference()
    {
        donut(adjustmentRingOuterDiameter, adjustmentRingInnerDiameter, height);
        
        translate( [0, 0, adjustmentRingGromitOffsetZ] )
            cylinder( d = adjustmentRingGromitVoidDiameter, h = adjustmentRingGromitVoidHeight);
    }
}

    
module adapter3Top()
{
    difference()
    {
        adapter3();
        
        removalHeight = adapter3PCBOffsetZ + adapter3PCBDimensions[2];
     
        translate( [0, 0, removalHeight/2 - manifoldCorrection] )
            cube( [adapter3FlangeDiameter + manifoldCorrection2, adapter3FlangeDiameter + manifoldCorrection2, removalHeight + manifoldCorrection2 * 2], center = true );
     }
}



module adapter3Bottom()
{
    difference()
    {
        adapter3();
        
        removalHeight2 = adapter3Height - (adapter3PCBOffsetZ + adapter3PCBDimensions[2]);
     
        translate( [0, 0, removalHeight2/2 + adapter3PCBOffsetZ + adapter3PCBDimensions[2]] )
            cube( [adapter3FlangeDiameter + manifoldCorrection2, adapter3FlangeDiameter + manifoldCorrection2, removalHeight2 + manifoldCorrection], center = true );
     }
}



module adapter3Cover()
{
    difference()
    {
        union()
        {
            difference()
            {
                union()
                {
                    donut(adapter3FlangeDiameter, adapter3InnerDiameter, adapter3CoverDepth);
                    
                    difference()
                    {
                        cylinder( d = adapter3InnerDiameter, h = fanVentHoleDiameter );
                        fanVent();
                    }

                    // Flex Collar Block
                    rotate( [-90, 0, 45] )
                        translate( [-flexCollarBlockDimensions[0]/2, -(flexCollarBlockDimensions[1] + fanVentHoleDiameter), - 1.9] )
                            cube( flexCollarBlockDimensions );

                    // Solid to fill in the fan vent around the collar block
                    rotate( [-90, 0, 45] )
                    {
                        translate( [-flexCollarBlockDimensions[0]/2, -fanVentHoleDiameter, - 1.9] )
                            cube( [flexCollarBlockDimensions[0], fanVentHoleDiameter, flexCollarBlockDimensions[2]] );
                        translate( [-flexCollarBlockDimensions[0]/2, -fanVentHoleDiameter, - (1.9 + fanVentHoleDiameter)] )
                            cube( [flexCollarBlockDimensions[0], fanVentHoleDiameter, fanVentHoleDiameter] );
                    }
                }
        
                for ( r = [0, 90, 180, 270] )
                {
                    rotate( [0, 0, r] )
                        translate( [adapter3TopBoltRadius, 0, 0] )
                        {
                            translate( [0, 0, adapter3CoverDepth - insertHoleDepth] )  
                                cylinder( d = insertHoleDiameter, h = insertHoleDepth + manifoldCorrection);
                            translate( [0, 0, -manifoldCorrection] )
                                cylinder( d = adapter3BoltDiameter, h = adapter3CoverDepth + manifoldCorrection2);
                        }   
                }

                // Highlight Ring
                translate( [0, 0, -manifoldCorrection] )
                    donut(highlightRingOuterDiameter, highlightRingInnerDiameter, highlightRingThickness + manifoldCorrection);
            
                // Cable Channel
                translate( [0, 0, 30] )
                    rotate( [-90, 0, 45] )
                    {
                        translate( [-cableThickness/2, 0, -manifoldCorrection - 1.9] )
                            cube( [cableThickness, caseOuterDiameter, caseMiddleHeight + manifoldCorrection] ); 
        
                        translate( [0, caseOuterDiameter/2 - flexCollarVoidThickness - caseThickness, collarVoidOffsetZ - 1.9] )
                        {
                            rotate( [0, 90, 90] )
                                lozenge(flexCollarVoidLength, flexCollarVoidWidth, flexCollarVoidThickness);
                        }
                    }
            }

            // Highlight Ring
            color( [0.0, 1.0, 0.0] )
                translate( [0, 0, -manifoldCorrection] )
                    donut(highlightRingOuterDiameter, highlightRingInnerDiameter, highlightRingThickness + manifoldCorrection);
        }
        
        translate( [0, 0, -fanVentHoleDiameter - manifoldCorrection2] )
            rotate( [-90, 0, 45] )
                translate( [-flexCollarBlockDimensions[0]/2, -(flexCollarBlockDimensions[1] + fanVentHoleDiameter), 20.1] )
                    cube( flexCollarBlockDimensions );

    }
}




module fanVent()
{
    hexagonSize = 4;
    hexagonBorder = 1.6;
    
    translate( [0, 0, -fanVentHoleDiameter * 0.5] )
        intersection()
        {
            translate( [hexagonSize, 0, 0] )
            {
                delta = (sqrt(hexagonSize)/2) * hexagonSize;
        
                for ( y = [-delta * 6:delta:delta * 6] )
                    for ( x = [-hexagonSize * 1.5 * 5:hexagonSize*1.5:hexagonSize * 1.5 * 5] )
                        translate( [x, y, 0] )
                            cylinder(d=hexagonSize-hexagonBorder/2, h=fanVentHoleDiameter * 2 + manifoldCorrection2, $fn=6);

                for ( y = [-delta * 6:delta:delta * 6] )
                    for ( x = [-hexagonSize * 1.5 * 5:hexagonSize * 1.5:hexagonSize * 1.5 * 5] )
                        translate( [x + hexagonSize * 1.5/2, y + delta*0.5, 0] )
                            cylinder(d=hexagonSize-hexagonBorder/2, h=fanVentHoleDiameter * 2 + manifoldCorrection2, $fn=6);
            }
        
            cylinder(d=fanVentDiameter, h=fanVentHoleDiameter * 2 + manifoldCorrection2);
        }
}



module adapter3()
{   
    difference()
    {
        union()
        {
            donut(inch2Diameter, adapter3InnerDiameter, adapter3Height);
            donut(adapter3FlangeDiameter, adapter3InnerDiameter, adapter3FlangeThickness);
            
            // Lens Flange
            translate( [0, 0, adapter3Height - adapter3LensFlangeThickness] )
                donut(inch2Diameter, adapter3LensFlangeInnerDiameter, adapter3LensFlangeThickness);
        }
        
        // Retention Lozenge
        translate( [-inch2Diameter/2, 0, adapter3Height/2 + adapter3FlangeThickness/2] )
            rotate( [0, 90, 0] )
                lozenge(adapter3RetentionHeight, adapter3RetentionWidth, adapter3RetentionDepth);
                
        // PCB
        translate( [0, 0, adapter3PCBOffsetZ] )
            translate( [0, 0, adapter3PCBDimensions[2]/2] )
                cube( adapter3PCBDimensions, center = true);
        
        // Bolt Holes
        heightTopToBoard = adapter3Height - adapter3PCBOffsetZ - adapter3PCBDimensions[2];
        for ( r = [15, 195, 285] )
            rotate( [0, 0, r] )
                translate( [(inch2Diameter + adapter3InnerDiameter) / 4, 0, 0] )
                {
                    translate( [0, 0, adapter3Height - (heightTopToBoard - adapter3BoltTopHeight)] )
                        cylinder(d = adapter3BoltHeadDiameter, h = heightTopToBoard - adapter3BoltTopHeight + manifoldCorrection);
                    translate( [0, 0, adapter3Height - (heightTopToBoard + adapter3PCBDimensions[2])] )
                        cylinder(d = adapter3BoltDiameter, h = heightTopToBoard + adapter3PCBDimensions[2] + manifoldCorrection);
                    translate( [0, 0, adapter3PCBOffsetZ - adapter3BoltThreadDepth] )
                        cylinder(d = adapter3BoltThreadDiameter, h = adapter3BoltThreadDepth + manifoldCorrection);
                }
                
        // PCB Corner Clearance Holes
        for ( r = [45, 135] )
            rotate( [0, 0, r] )
                translate( [0, 0, adapter3PCBClearanceDimensions[2]/2 + adapter3PCBOffsetZ + adapter3PCBDimensions[2]/2 - adapter3PCBClearanceDimensions[2]/2] )
                    cube( adapter3PCBClearanceDimensions, center = true);
                    
         // Top Bolt Holes
        for ( r = [0, 90, 180, 270] )
        {
            rotate( [0, 0, r] )
                translate( [adapter3TopBoltRadius, 0, 0] )
                {
                    translate( [0, 0, adapter3FlangeThickness - (adapter3BoltHeadHeight + 0.5)] )  
                        cylinder( d2=adapter3BoltHeadDiameter, d1 = adapter3BoltDiameter, h = (adapter3BoltHeadHeight + 0.5) + manifoldCorrection);
                    translate( [0, 0, -manifoldCorrection] )
                        cylinder( d = adapter3BoltDiameter, h = adapter3FlangeThickness + manifoldCorrection2);
                }
         }
         
         translate( [0, 19, -adapter3CableClearanceBlock[2]/2 + adapter3PCBOffsetZ] )
            cube( adapter3CableClearanceBlock, center = true);
     }
     
     // PCB Posts
     halfAdapter3PCBPostHolesDistance = adapter3PCBPostHolesDistance/2;
     for ( pos = [ [-halfAdapter3PCBPostHolesDistance, -halfAdapter3PCBPostHolesDistance],
                  [-halfAdapter3PCBPostHolesDistance,  halfAdapter3PCBPostHolesDistance],
                  [ halfAdapter3PCBPostHolesDistance, -halfAdapter3PCBPostHolesDistance],
                  [ halfAdapter3PCBPostHolesDistance,  halfAdapter3PCBPostHolesDistance] ] )
        translate( [pos[0], pos[1], adapter3PCBOffsetZ - adapter3PCBClearanceDimensions[2]/2] )
            cylinder(d = adapter3PCBPostDiameter, h = adapter3PCBDimensions[2] + adapter3PCBClearanceDimensions[2]/2);
}
    

module adapter1()
{
    donut(inch2Diameter, cameraDiameter, adapter1Height);
    donut(adapter1FlangeDiameter, cameraDiameter, adapter1FlangeThickness);
}



module adapter2()
{
    difference()
    {
        donut(inch2Diameter, cameraDiameter, adapter2Height);
        translate( [0, 0, adapter2CollarZOffset] )
            donut(inch2Diameter + 1.0, adapter2CollarDiameter, adapter2CollarHeight);
    }
    
    translate( [0, 0, adapter2CollarHeight + adapter2CollarZOffset - adapter2CollarBevelHeight] )
        difference()
        {
            cylinder(d2 = inch2Diameter, d1 = adapter2CollarDiameter, h = adapter2CollarBevelHeight);
            translate( [0, 0, -manifoldCorrection] )
                cylinder(d = cameraDiameter, h = adapter2CollarBevelHeight + manifoldCorrection2);
        }
}



module donut(outerDiameter, innerDiameter, height)
{
    difference()
    {
        cylinder(d=outerDiameter, h=height);
        translate( [0, 0, -manifoldCorrection] )
            cylinder(d=innerDiameter, h=height + manifoldCorrection * 2);
    }
}



module lozenge(length, width, height)
{
    hull()
    {
        translate( [-(length-width)/2, 0, 0] )
            cylinder(d=width, h=height);
        translate( [(length-width)/2, 0, 0] )
            cylinder(d=width, h=height);
    }
}