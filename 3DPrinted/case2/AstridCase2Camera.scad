// Black ASA Filament
//  Bambu Labs:
//      Print partNum 4 (Plate)
//      
//      Filament Color:  Main: ASA Black, Highlight Only: ASA Green (closer to Turquoise)
//      Drying:          ASA will need drying before use, it comes from Bambu Labs too wet to print well.  
//                         12hrs should be enough at 70C (ASA setting on Creality)
//      AMS Compatible:  Yes (need to make sure descicant is dry in AMS)
//      Plate:           Smooth PEI Plate
//      Bed Temperature: 110C (yes, 10C over)
//      Bed Adhesion:    Bambu Liquid Glue
//      Support:         Yes
//      Infill:          25%
//      Bambu Studio:    After import, change highlight color for ring to Green

//      Print partNum 3 (Flex Collars)
//      
//      Filament Color:  Main: ASA Black
//      Drying:          ASA will need drying before use, it comes from Bambu Labs too wet to print well.  
//                         12hrs should be enough at 70C (ASA setting on Creality)
//      AMS Compatible:  Yes (need to make sure descicant is dry in AMS)
//      Plate:           Smooth PEI Plate
//      Bed Temperature: 110C (yes, 10C over)
//      Bed Adhesion:    Bambu Liquid Glue
//      Support:         No
//      Infill:          100%

// Post Processing:
//      - Remove support
//      - Wash adhesive off parts
//      - Dry parts
//      - Insert 4 heat inserts in bottom case, with drill press / soldering iron/ supplied heat tool, just below surface
//        (Uses 4 x   M2.5x3.5x4 Hanglife Inserts HLTI-M2.5-SET01)
//      - Remove white haze on cases where there was plate contact with heat gun


partNum                             = 3;        // 0 = All, 1 = Bottom, 2 = Top, 3 = Flex Collars, 4 = Plate


caseThickness                       = 1.2;

caseInnerDiameter                   = 56.57;
caseOuterDiameter                   = caseInnerDiameter + caseThickness*2;

pcbDimensions                       = [39.1, 39.1, 1.60];

cableWidth                          = 17.0;
cableThickness                      = 3.0;
pcbConnectorHeight                  = 3.4;
caseMiddleHeight                    = pcbDimensions[2] + pcbConnectorHeight + cableWidth + 0.5;

pcbSupportWidth                     = 6.4;
pcbSupportWidthRadius               = 24.0;

insertHoleDiameter                  = 3.2 + 0.2;
insertHoleDepth                     = 5.0;
boltHoleDiameter                    = 2.6 + 0.3;
boltHeadDiameter                    = 4.5 + 0.2;
boltHeadHeight                      = 1.6;

cameraFlangeInnerDiameter           = 30.0;
cameraFlangeHeight                  = 11.0;
cameraInternalDiameter              = 51.0;
cameraVoidHeight                    = 3.0;

markerDepth                         = 0.8;
markerWidth                         = 1.2;
markerLength                        = 5.0;

fanVentDiameter                     = 40.0;

highlightRingOuterDiameter          = caseOuterDiameter - 7.0;
highlightRingInnerDiameter          = highlightRingOuterDiameter - 5.0;
highlightRingThickness              = 0.8;

flexCollarDepth                     = 6.0;
flexCollarSurroundThickness         = 1.0;

flexThickness                       = 0.7;  // The overall thickness of the tube as it ships (both sides)

flexOuterLength                     = cableWidth + flexCollarSurroundThickness * 2;
flexOuterWidth1                     = cableThickness + flexCollarSurroundThickness * 2;
flexOuterWidth2                     = flexOuterWidth1 - 1.0;

flexOuterClampWidth1                = flexOuterWidth1 + flexThickness;
flexOuterClampWidth2                 = flexOuterWidth2 + flexThickness;

flexOuterClampOuterBorder           = 1.5;
flexOuterClampInnerLength           = flexOuterLength + flexThickness;
flexOuterClampOuterWidth            = flexOuterClampWidth1 + flexOuterClampOuterBorder;
flexOuterClampOuterLength           = flexOuterLength + flexThickness + flexOuterClampOuterBorder;

flexCollarVoidLength                = flexOuterClampOuterLength + 1.8;
flexCollarVoidWidth                 = flexOuterClampOuterWidth + 0.5;
flexCollarVoidThickness             = flexCollarDepth + 0.75;
flexCollarMarkerWidth               = 1.0;

collarVoidOffsetZ                   = 12.0;

flexCollarBlockDimensions           = [10.7, flexCollarVoidThickness + 1.75, caseMiddleHeight];
flexCollarBlockOffsetY              = -1.0;

manifoldCorrection                  = 0.01;
manifoldCorrection2                 = manifoldCorrection * 2;

$fn                                 = 160;



if (partNum == 0 || partNum == 1 )
{
    rotate( [0, 180, 0] )
        caseBottom();
}

if ( partNum == 0 || partNum == 2 )
{
    caseMiddle();
    caseTop();
}

if ( partNum == 0 || partNum == 3 )
{
    translate( [32, 13, 0] )
        rotate( [0, 0, 90] )
            flexCollar1();
    translate( [32, -13, 0] )
        rotate( [0, 0, 90] )
            flexCollar1();

    translate( [32, 27, 0] )
        flexCollar2();
    translate( [32, -27, 0] )
            flexCollar2();
}

if ( partNum == 4 )
{
    caseBottom();
    translate( [caseOuterDiameter + 5.0, 0, caseMiddleHeight + caseThickness] )
        rotate( [0, 180, 0] )
        {
            caseMiddle();
            caseTop();
        }
}






module flexCollar1()
{
    difference()
    {
        lozengeConical(flexOuterLength, flexOuterWidth1, flexOuterWidth2, flexCollarDepth);
        translate( [0, 0, -manifoldCorrection] )
            lozenge(cableWidth, cableThickness, flexCollarDepth + manifoldCorrection2);
            
        // Marker
        translate( [-flexCollarMarkerWidth/2, 0, -manifoldCorrection] )
            cube( [flexCollarMarkerWidth, flexOuterWidth1, flexCollarMarkerWidth/2 + manifoldCorrection] );
    }
}



module flexCollar2()
{
    translate( [0, 0, flexCollarDepth] )
        rotate( [180,0, 0] )
            difference()
            {
                lozenge(flexOuterClampOuterLength, flexOuterClampOuterWidth, flexCollarDepth);
                translate( [0, 0, -manifoldCorrection] )
                    lozengeConical(flexOuterClampInnerLength, flexOuterClampWidth1 + manifoldCorrection, flexOuterClampWidth2, flexCollarDepth + manifoldCorrection2);
                
                // Marker
                translate( [-flexCollarMarkerWidth/2, 0, -manifoldCorrection] )
                    cube( [flexCollarMarkerWidth, flexOuterClampOuterWidth + manifoldCorrection, flexCollarMarkerWidth/2 + manifoldCorrection] );
            }
}



module caseBottom()
{
    difference()
    {
        union()
        {
            donut(caseOuterDiameter, cameraInternalDiameter, cameraVoidHeight);
            translate( [0, 0, cameraVoidHeight] )
                donut(caseOuterDiameter, cameraFlangeInnerDiameter, caseThickness);

            translate( [0, 0, cameraVoidHeight] )
                donut( cameraFlangeInnerDiameter + 5.0, cameraFlangeInnerDiameter, cameraFlangeHeight - cameraVoidHeight);
        
            // PCB Supports
            for ( r = [45, 135, 225, 315] )
                rotate( [0, 0, r] )
                    translate( [0, pcbSupportWidthRadius, 0] )
                    {
                        difference()
                        {
                            union()
                            {
                                // The support
                                cylinder(d = pcbSupportWidth, h = cameraVoidHeight);
                                translate( [-pcbSupportWidth/2, 0, 0] )
                                    cube( [pcbSupportWidth, caseInnerDiameter/2 - pcbSupportWidthRadius, cameraVoidHeight] );
                            }
                       }
                    }
        }
            
        // Bolt Holes
        for ( r = [45, 135, 225, 315] )
            rotate( [0, 0, r] )
                translate( [0, pcbSupportWidthRadius, 0] )
                {
                    // Bolt hole
                    translate( [0, 0, -manifoldCorrection] )
                        cylinder(d = boltHoleDiameter, h = cameraVoidHeight + caseThickness + manifoldCorrection2); 
                        
                    // Bolt head hole
                    translate( [0, 0, cameraVoidHeight + caseThickness - boltHeadHeight] )
                        cylinder(d2=boltHeadDiameter, d1=boltHoleDiameter, h=boltHeadHeight + manifoldCorrection);
                }
                
         // Marker
         rotate( [0, 0, 180] )
            translate( [-markerWidth/2, caseOuterDiameter/2 - markerLength + manifoldCorrection, cameraVoidHeight + caseThickness - markerDepth] )
                cube( [markerWidth, markerLength, markerDepth + manifoldCorrection] );
     }
}



module caseMiddle()
{
    difference()
    {
        union()
        {
            donut(caseOuterDiameter, caseInnerDiameter, caseMiddleHeight);
        
            // Flex Collar Block
            translate( [-flexCollarBlockDimensions[0]/2, caseOuterDiameter/2 - flexCollarBlockDimensions[1] + flexCollarBlockOffsetY, 0] )
                cube( flexCollarBlockDimensions );
        }
        
        // Cable Channel
        translate( [-cableThickness/2, 0, -manifoldCorrection] )
            cube( [cableThickness, caseOuterDiameter, caseMiddleHeight + manifoldCorrection] ); 
        
        translate( [0, caseOuterDiameter/2 - flexCollarVoidThickness - caseThickness, collarVoidOffsetZ] )
        {
            rotate( [0, 90, 90] )
                lozenge(flexCollarVoidLength, flexCollarVoidWidth, flexCollarVoidThickness);
            translate( [0, 0, -flexCollarVoidLength/2] )
                rotate( [0, 90, 90] )
                    lozenge(flexCollarVoidLength, flexCollarVoidWidth, flexCollarVoidThickness);
        }
    }
    
    // PCB
    //translate( [0, 0, pcbDimensions[2] / 2] )
    //    cube(pcbDimensions, center = true);
        
    // PCB Supports
    translate( [0, 0, pcbDimensions[2]] )
        for ( r = [45, 135, 225, 315] )
            rotate( [0, 0, r] )
                pcbSupport();
}



module caseTop()
{
    translate( [0, 0, caseMiddleHeight] )
    {
        difference()
        {
            cylinder(d = caseOuterDiameter, h = caseThickness);
            fanVent();
            
            // Highlight Ring
            translate( [0, 0, caseThickness - highlightRingThickness] )
                donut(highlightRingOuterDiameter, highlightRingInnerDiameter, highlightRingThickness + manifoldCorrection);
        }

        // Highlight Ring
        translate( [0, 0, caseThickness - highlightRingThickness] )
            donut(highlightRingOuterDiameter, highlightRingInnerDiameter, highlightRingThickness);
    }
}



module fanVent()
{
    hexagonSize = 4;
    hexagonBorder = 1.6;
    
    translate( [0, 0, -caseThickness * 0.5] )
        intersection()
        {
            translate( [hexagonSize, 0, 0] )
            {
                delta = (sqrt(hexagonSize)/2) * hexagonSize;
        
                for ( y = [-delta * 6:delta:delta * 6] )
                    for ( x = [-hexagonSize * 1.5 * 5:hexagonSize*1.5:hexagonSize * 1.5 * 5] )
                        translate( [x, y, 0] )
                            cylinder(d=hexagonSize-hexagonBorder/2, h=caseThickness * 2 + manifoldCorrection2, $fn=6);

                for ( y = [-delta * 6:delta:delta * 6] )
                    for ( x = [-hexagonSize * 1.5 * 5:hexagonSize * 1.5:hexagonSize * 1.5 * 5] )
                        translate( [x + hexagonSize * 1.5/2, y + delta*0.5, 0] )
                            cylinder(d=hexagonSize-hexagonBorder/2, h=caseThickness * 2 + manifoldCorrection2, $fn=6);
            }
        
            cylinder(d=fanVentDiameter, h=caseThickness * 2 + manifoldCorrection2);
        }
}



module pcbSupport()
{
    supportHeight = caseMiddleHeight - pcbDimensions[2];

    translate( [0, pcbSupportWidthRadius, 0] )
    {
        difference()
        {
            union()
            {
                // The support
                cylinder(d = pcbSupportWidth, h = supportHeight);
                translate( [-pcbSupportWidth/2, 0, 0] )
                    cube( [pcbSupportWidth, caseInnerDiameter/2 - pcbSupportWidthRadius, supportHeight] );
            }
            
            // Bolt hole
            translate( [0, 0, -manifoldCorrection] )
                cylinder(d = boltHoleDiameter, h = supportHeight + manifoldCorrection2);
                
            // Insert hole
            translate( [0, 0, -manifoldCorrection] )
                cylinder(d = insertHoleDiameter, h = insertHoleDepth + manifoldCorrection);
        }
    }
}


module donut(outerDiameter, innerDiameter, height)
{
    difference()
    {
        cylinder(d = outerDiameter, h = height);
        translate( [0, 0, -manifoldCorrection] )
            cylinder(d = innerDiameter, h = height + manifoldCorrection2);
    }
}



module lozenge(length, width, height)
{
    hull()
    {
        translate( [-(length - width)/2, 0, 0] )
            cylinder(d = width, h = height);
        translate( [(length - width)/2, 0, 0] )
            cylinder(d = width, h = height);
    }
}



// width1 must be larger than width2
// length is the largest length

module lozengeConical(length, width1, width2, height)
{
    lengthMajor = (length - width1)/2;
    lengthMinor = ((length - (width1 - width2)) - width2) / 2;
    
    hull()
    {
        hull()
        {
            translate( [-lengthMajor, 0, 0] )
                cylinder(d = width1, h = manifoldCorrection);
            translate( [lengthMajor, 0, 0] )
                cylinder(d = width1, h = manifoldCorrection);
        }
        
        hull()
        {
            translate( [-lengthMinor, 0, height - manifoldCorrection] )
                cylinder(d = width2, h = manifoldCorrection);
            translate( [lengthMinor, 0, height - manifoldCorrection] )
                cylinder(d = width2, h = manifoldCorrection);
        }
    }
}