// Black Filament:  Black filament often contains Carbon Black as an ingredient. Carbon blocks/attenuates Radio
// Frequencies, so isn't the best choice for GPS and Wifi.  Test for your application or use another color.

// Camera holder print settings:
//      Resin: (print on plate, no raft, 0 Height From Raft)
//              Lychee Slicer:
//                  Anti-aliasing: Smooth Surfaces
//                  Auto lift: Off
//                  Supports Density: Ultra
//                  Auto Supports: Light
//                  Raft: None
//                  Flashforge Washable Grey:
//                      Initial Exposure: 14s
//                      Turn off Delay: 2s
//                      Exposure Time: 2.1s
//                      Rising Height: 8mm
//                      Motor Speed: 5mm/s
//                      Bottom Exposure Layer: 1

// Plate 6 print settings:
//      Resin: (print on plate, no raft, 0 Height From Raft)
//              Lychee Slicer:
//                  Anti-aliasing: Smooth Surfaces
//                  No support, no rafts
//                  Flashforge Washable Grey:
//                      Initial Exposure: 14s
//                      Turn off Delay: 2s
//                      Exposure Time: 2.1s
//                      Rising Height: 8mm
//                      Motor Speed: 5mm/s
//                      Bottom Exposure Layer: 1

// However for the best Resin print, set to Plate 6, print in orientation set, i.e. flat side down.

// Hardware (Threads are M2.5 x 0.45mm):
//      Bolts: (12) M2.5 x 14mm Countersunk Phillips
//      Nuts:  (12) M2.5 (5.8mm Head Diameter)
//      Standoffs: (4) M2.5 x 14mm

// ***** ROTATE HEADERS SO THEY COME INBOARD NOT OUTBOARD OR SWITCH TO SCREW TERMINALS (PROBABLY BETTER)
// ***** 12V SUPPLY ON BOARD, FET FOR PELTIER

// TODO:
// Longer flat flex
// Double sided adhesive tape
// Camera deformation

// THESE MAY NEED CHANGING, IF THERE ARE CLEARANCE ISSUES, OR HADRDWARE DIFFERENCES
partNum                     = 10;            // 0 = All, 1 = Camera Holder, 2 = Camera Posts, 3 = Bottom Case, 4 = Top Case, 5 = Plate (without camera, may not work), 6 = Plate (works), 7 = Gps and Camera washers, 8 = Fan Cover, 9 = Gps and Camera Washers x 56, 10 = Logo
logoNum                     = 3;            // 1 = Eclipse (short text), 2 = Eclipse (full text), 3 = Asteroid Occultation
externalGps                 = true;         // Make a whole for an external GPS if true
nutDiameter                 = 5.8 + 0.2;    // This is point to point
nutThickness                = 2.0;
boltHeadDiameter            = 4.5;
boltHeadHeight              = 1.6;
boltHoleDiameter            = 2.6;
clearancePiX                = 0.5;          // Clearance around the raspberry Pi in the X axis
clearancePiY                = 3.5;          // Clearance around the raspberry Pi in the Y axis
caseSideThickness           = 2.0;
caseBoltLength              = 13 + 7.68;
caseBoltHoleInset           = 17.0;         // Inset from the corner of caseOuterBorder below
casePCBToTopHatHeight       = 35;           // This distance from the the bottom of the Pi PCB to the top of the electronics(hats) + fan thickness plus any clearance for flow

caseBottomPiClearance       = 3.0;          // Clearance between the bottom of the case Pi PCB
caseBottomTopThickness      = 3.0;          // Thickness of the bottom and top of the case
piBoardDimensions           = [85, 56, 1.5, 3.5];
caseBottomPiHoleOuterDia    = 6.0;          // Outside of the boltHoleDiameter
caseOuterBorder             = [piBoardDimensions[0] + 40, piBoardDimensions[1] + 40, 1];
caseOuterInset              = [85 + (clearancePiX + caseSideThickness) * 2, 56 + (clearancePiY + caseSideThickness) * 2, 1];
caseOuterBorderRadius       = 5.0;
caseOuterInsetRadius        = 20.0;
caseOuterInsetInset         = 10;
fanCenterPosition           = [-piBoardDimensions[0]/2 + 21, 10];
fanDimensions               = [30.4, 30.4, 8.1];
fanCoverDimensions          = [30, 30, 2.0];
fanCoverRecessDiameter      = 29.0;
fanHolePositionXY           = 12;
fanPostDiameter             = 2.6;
fanCoverPostHoleDiameter    = fanPostDiameter + 0.2;
fanCoverThickness           = 2.0;
fanPostHeight               = 8.1 + fanCoverDimensions[2];
fanVentDiameter             = 28.5;
fanClipThickness            = 1;
fanClipWidth                = 10;
fanClipRoundThickness       = 0.7;

fanClipHeight               = fanDimensions[2] + fanCoverDimensions[2] + fanClipRoundThickness * 2;
sideVentDiamondSize         = 1.0;
sideVentDiamondSpacing      = 2.0;
sideVentHeight              = 25;
        


// BELOW HERE, THESE LIKELY DON'T NEED CHANGING
// Raspberry Pi 4B Dimensions
manifoldCorrection          = 0.01;
cameraBoltHoleOffset        = 17;
cameraPCBThickness          = 3.4;
cameraPCBBottomClearance    = 3.7;
cameraTopCaseThickness      = 3;
cameraVoidDimensions        = [40.5 + 1, 40.5+16.5, cameraPCBBottomClearance + cameraPCBThickness];
cameraBlockDimensions       = [39 + 5, caseOuterInset[1], cameraPCBBottomClearance + cameraPCBThickness + cameraTopCaseThickness];
cameraPostDiameter          = 6;
cameraPostHeight            = (cameraVoidDimensions[2] - cameraPCBThickness) - 0.2 + 1.6;
cameraPostInnerLipDiameter  = cameraPostDiameter - 1.0;
cameraPostLipThickness      = 0.2;
cameraPostRecessDonut       = [cameraPostDiameter + 0.2, cameraPostInnerLipDiameter - 0.2, cameraPostLipThickness + 0.2];
cameraMountInnerDiameter    = 33.3;
cameraMountOuterDiameter    = cameraBlockDimensions[0] - 3.2;
cameraMountDepth            = 10 - cameraTopCaseThickness; 
cameraBoltHoleDepth         = cameraMountDepth + 0.25;
cameraNutHoleDepth          = nutThickness - 1;
cameraRotationIndentXY      = [0.75, 0.5];
cameraHoleReinforcementDia  = 8;
cameraHoleReinforcementDistance = cameraBoltHoleOffset + 7;
cameraVoidSupportThickness  = 0.8;
cameraVentDimensions        = [2.0, 2.0, 5.0];
cameraVentTopDiameter       = 2.0;
caseCamCableHoleDimensions  = [25, 6];
caseCamCableHoleOffsetY     = 24.45;
mountExtensionInner         = [27, 5, 2];
mountExtensionToInside      = 10;
mountExtensionOuter         = [28, 8, cameraMountDepth];
sideVent1                   = [[0, caseOuterInset[1]/2 - caseSideThickness/2, sideVentHeight], 55, 10];     // [[CenterPosition], length, height]
sideVent2                   = [[0, -(caseOuterInset[1]/2 - caseSideThickness/2), sideVentHeight], 55, 10];
sideVent3                   = [[0, caseOuterInset[0]/2 - caseSideThickness/2, sideVentHeight], 30, 10];
punchOutCase                = 5.5;
portRecessDepth             = 1.0;
portRecess2Dimensions       = [16+4, 10, 15+6];
portRecess2Pos              = [-27.7, -caseOuterInset[0]/2 - portRecess2Dimensions[1],5.2];
portRecess3Dimensions       = [16+4, 10, 15+3.5];
portRecess3Pos              = [7.5, -caseOuterInset[0]/2 - portRecess3Dimensions[1],5.2];
portRecess4Dimensions       = [12, 10, 2.25 + 4];
portRecess4Pos              = [-portRecess4Dimensions[0]/2, -caseOuterInset[0]/2 - portRecess4Dimensions[1] + caseSideThickness/2, -portRecess4Dimensions[2] / 2 + caseBottomPiClearance + caseBottomTopThickness - (0.32 + 2.25/4)];
caseSplitHeight             = caseBottomTopThickness + caseBottomPiClearance + 4.75 + 7.68;
piBoardHoleLocation         = [ [3.5, 3,5], [3.5, 3.5+49], [3.5+58, 3.5], [3.5+58, 3.5+49] ];
piBoardSDCardSlotDimensions = [2.5 + punchOutCase, 12, 2.25];
piBoardSDCardSlotPosZ       = 0.32;
piBoardSDCardSupportDiameter= 0.8;
piBoardSDCardSupportLocs    = [-3, 0, 3];
sdCardSupportPos            = [-(piBoardDimensions[0]/2 + clearancePiX) - 0.5, 0, 0];
piBoardHeaderDimensions     = [51.15, 4.9, 12.0];
piBoardHeaderPos            = [3.5+29-piBoardHeaderDimensions[0]/2, piBoardDimensions[1]-(3.5 + piBoardHeaderDimensions[1]/2), 0];
piBoardUSB1Dimensions       = [14.8, 3.18 + punchOutCase, 16.5];
piBoardUSB1Position         = 9;
piBoardUSB2Dimensions       = [14.5, 3.18 + punchOutCase, 16.5];
piBoardUSB2Position         = 27;
piBoardEtherDimensions      = [16.0, 3.18 + punchOutCase, 13.75];
piBoardEtherPosition        = 45.75;
piBoardLED1Dimensions       = [1.2, 3 + punchOutCase, 1.3];
piBoardLED2Dimensions       = [1.2, 3 + punchOutCase, 1.3];
piBoardLED1Position         = [8.0, -0.4];
piBoardLED2Position         = [11.65, -0.4];
timingBoardReinforcementThickness = 3;
timingBoardJackDimensions   = [11.25, 1.25 + punchOutCase, 13.5];
timingBoardJackPos          = [3.5+10.47, 0, 10 + 1.17];
xvsLeadChannelDimensions    = [2, 2, 20];
xvsLeadChannelPos           = [-38, +(piBoardDimensions[1] + clearancePiY * 2)/2 - manifoldCorrection, caseBottomTopThickness];


caseNutDepth                = caseSplitHeight - 2;
caseHeight = caseBottomTopThickness + caseBottomPiClearance + casePCBToTopHatHeight + caseBottomTopThickness;

raspberryPiPortClearance    = 0.25;

logoDepth                   = 1;
logo1Pos                    = [15, 0];
logo2Pos                    = [25, 0];
logo3Pos                    = [19, 0];

gpsExternalCableHoleDiameter= 6.5;
gpsExternalCableZPosZ       = caseBottomTopThickness + 4.55;    // This is the distance from the top of the case

cameraWasherDimensions      = [5.0, 2.6, 1.0];
gpsWasherDimensions         = [6.0, 3.0, 2.4];
gpsWasherLozengeDimensions  = [21.0, 4.0, gpsWasherDimensions[2]];
gpsWasherLozengeRetainerDimensions = [15.0, 1.56, 1.5];

$fn                         = 80;

include <polyround.scad>
use <junegull/junegull.ttf>
use <PoetsenOne-Regular.ttf>



if ( partNum == 0 || partNum == 1 ) cameraHolder();
if ( partNum == 0 || partNum == 2 ) cameraPosts();
if ( partNum == 0 || partNum == 3 ) piCaseBottom();
if ( partNum == 0 || partNum == 4 ) piCaseTop();
    
if ( partNum == 5 )
{
    translate( [0, 0, caseSplitHeight] )
        rotate( [180, 0, 0] )
        {
            piCaseBottom();
            cameraPosts();
        }
    
    translate( [0, caseOuterBorder[1] - 20, -caseSplitHeight] ) 
        piCaseTop();
}

if ( partNum == 6 )
{
    translate( [0, 0, 0] )
        piCaseBottom();
    
    translate( [0, 40.5, 0] )
        rotate( [0, 180, 0] )
            cameraPostsLine();
    
    translate( [-15, -43, 0] )
        cameraGpsWashers();
    
    translate( [0, caseOuterBorder[1] - 15, caseHeight - caseSplitHeight] ) 
        rotate( [180, 0, 0] )
            translate( [0, 0, -caseSplitHeight] ) 
                piCaseTop();
    
    translate( [20, -51, 0] )
        fanCover();
}

if ( partNum == 7 ) cameraGpsWashers();
    
if ( partNum == 8 ) fanCover();

if ( partNum == 9 ) cameraGpsWashersX56();

if ( partNum == 10 )    logo3();


//translate( [-piBoardDimensions[0]/2, -piBoardDimensions[1]/2, caseBottomTopThickness + caseBottomPiClearance] )
//    raspberryPi4BModel();


module fanCover()
{
    difference()
    {
        roundedRect(fanCoverDimensions[0], fanCoverDimensions[1], fanCoverThickness, 3);
        translate( [0, 0, fanCoverThickness/2 + manifoldCorrection] )
            cylinder( d = fanCoverRecessDiameter, h = fanCoverThickness/2 );
        
            // Fan Posts
        for ( pos = [
            [fanHolePositionXY,   fanHolePositionXY],
            [-fanHolePositionXY,  fanHolePositionXY],
            [fanHolePositionXY,  -fanHolePositionXY],
            [-fanHolePositionXY, -fanHolePositionXY],
            ] )
        {
            translate( [pos[0], pos[1], -manifoldCorrection] )
            {
                cylinder(d=fanCoverPostHoleDiameter, h=fanCoverThickness + manifoldCorrection * 2);
            }
        }
        
        fanVent();
    }
}


module cameraGpsWashers()
{
    //translate( [0, 0, 0] )
    //    donut(cameraWasherDimensions[0], cameraWasherDimensions[1], cameraWasherDimensions[2]);
    //translate( [10, 0, 0] )
    //    donut(cameraWasherDimensions[0], cameraWasherDimensions[1], cameraWasherDimensions[2]);
    //translate( [20, 0, 0] )
    //    donut(cameraWasherDimensions[0], cameraWasherDimensions[1], cameraWasherDimensions[2]);            
    //translate( [30, 0, 0] )
    //    donut(cameraWasherDimensions[0], cameraWasherDimensions[1], cameraWasherDimensions[2]);

    translate( [-10, 0, 0] )
        donut(gpsWasherDimensions[0], gpsWasherDimensions[1], gpsWasherDimensions[2]);
    translate( [-20, 0, 0] )
        donut(gpsWasherDimensions[0], gpsWasherDimensions[1], gpsWasherDimensions[2]);
    
    translate( [0, -10, 0] )
    {
        lozenge(gpsWasherLozengeDimensions[0], gpsWasherLozengeDimensions[1], gpsWasherLozengeDimensions[2]);
        translate( [0, 0, gpsWasherLozengeDimensions[2]] )
            lozenge(gpsWasherLozengeRetainerDimensions[0], gpsWasherLozengeRetainerDimensions[1], gpsWasherLozengeRetainerDimensions[2]);
    }
}



module cameraGpsWashersX56()
{
    for (x = [0:40:120] )
        for (y = [0:8:105])
        {
            translate( [x, y, 0] )
            {
                translate( [-15, 0, 0] )
                    donut(gpsWasherDimensions[0], gpsWasherDimensions[1], gpsWasherDimensions[2]);
                translate( [-25, 0, 0] )
                    donut(gpsWasherDimensions[0], gpsWasherDimensions[1], gpsWasherDimensions[2]);
    
                translate( [0, 0, 0] )
                {
                    lozenge(gpsWasherLozengeDimensions[0], gpsWasherLozengeDimensions[1], gpsWasherLozengeDimensions[2]);
                    translate( [0, 0, gpsWasherLozengeDimensions[2]] )
                        lozenge(gpsWasherLozengeRetainerDimensions[0], gpsWasherLozengeRetainerDimensions[1], gpsWasherLozengeRetainerDimensions[2]);
                }
            }
        }
}



module clip(width, thickness, height, roundThickness)
{
    translate( [0, 0, height/2] )
        cube( [width, thickness, height], center = true );
    
    translate( [0, thickness / 2, height - roundThickness] )
        rotate( [0, 90, 0] )
            cylinder(d=roundThickness * 2, width, center = true);
}



module logo1()
{
    translate( [logo1Pos[0], logo1Pos[1], -logoDepth + manifoldCorrection] )
    {
        difference()
        {
            cylinder(d=30, h = logoDepth);
            translate( [-20, 0, -manifoldCorrection] )
                cylinder(d=50, h = logoDepth + manifoldCorrection * 2);
        }
        translate( [-2, -0.6, 0] )
            linear_extrude(logoDepth + manifoldCorrection)
                text("ASTRID", size=5.2, font="junegull", direction="ttb", spacing=1.3, halign="center", valign="center");
    }
}



module logo2()
{
    fontSize        = 4.5;
    fontSpacing     = 1.3;
    textPositionX   = -26.5;
    
    translate( [logo2Pos[0], logo2Pos[1], -logoDepth + manifoldCorrection] )
    {
        difference()
        {
            cylinder(d=30, h = logoDepth);
            translate( [-20, 0, -manifoldCorrection] )
                cylinder(d=50, h = logoDepth + manifoldCorrection * 2);
        }

        translate( [textPositionX, 7, 0] )
            linear_extrude(logoDepth + manifoldCorrection)
                text("ASTRo", size=fontSize, font="PoetsenOne", spacing=fontSpacing, halign="left", valign="center");

        translate( [textPositionX, 0, 0] )
            linear_extrude(logoDepth + manifoldCorrection)
                text("Imaging", size=fontSize, font="PoetsenOne", spacing=fontSpacing, halign="left", valign="center");

        translate( [textPositionX, -7, 0] )
            linear_extrude(logoDepth + manifoldCorrection)
                text("Device", size=fontSize, font="PoetsenOne", spacing=fontSpacing, halign="left", valign="center");
    }
}



module logo3()
{
    translate( [logo3Pos[0], logo3Pos[1], -logoDepth + manifoldCorrection] )
    {
        difference()
        {
            union()
            {
                logo3Line(-17.0, 1.5);
                logo3Line(-14.1, 1.5);
                logo3Line(-10.0, 1.5);
                logo3Line(-4.4, 1.5);
                logo3Line(0, 1.5);
                logo3Line(3, 1.5);
                logo3Line(9.0, 1.5);
                logo3Line(14.1, 1.5);
                logo3Line(17.0, 1.5);

                rotate( [0, 0, 15] )
                    scale( [1.8, 1.0, 1.0] )
                        cylinder(d=15, h=logoDepth + manifoldCorrection);
            }
            
            translate( [0.5, 0, 0] )
                linear_extrude(logoDepth + manifoldCorrection)
                    text("ASTRID", size=4.0, font="PoetsenOne", spacing=1.3, halign="center", valign="center");
        }

    }
}


module logo3Line(offsetY, thickness)
{
    translate( [0, offsetY, 0] )
        rotate( [0, 0, -30] )
            translate( [0, 0, (logoDepth + manifoldCorrection)/2 + manifoldCorrection/2] )
                cube( [40, thickness, logoDepth + manifoldCorrection], center=true );
}



module cameraPosts()
{
    // Camera Posts
    for ( pos = [
        [cameraBoltHoleOffset,   cameraBoltHoleOffset],
        [-cameraBoltHoleOffset,  cameraBoltHoleOffset],
        [cameraBoltHoleOffset,  -cameraBoltHoleOffset],
        [-cameraBoltHoleOffset, -cameraBoltHoleOffset],
        ] )
        translate( [pos[0], pos[1], -cameraVoidDimensions[2] + cameraPCBThickness] )
            cameraPost();
}



module cameraPostsLine()
{
    // Camera Posts
    for ( pos = [
        [0, 0],
        [-10, 0],
        [-20, 0],
        [-30, 0],
        [10, 0],
        [20, 0],
        [30, 0],
        ] )
        translate( [pos[0], pos[1], 0] )
            rotate( [0, 180, 0] )
                cameraPost();
}



module cameraPost()
{
    donut(cameraPostDiameter, boltHoleDiameter, cameraPostHeight);
    translate( [ 0, 0, cameraPostHeight] )
        donut(cameraPostDiameter, cameraPostInnerLipDiameter, cameraPostLipThickness);
}

    
    
module cameraHolder()
{
    // Main Block
    difference()
    {
        union()
        {
            difference()
            {
                // Main Block
                translate( [0, 0, -cameraBlockDimensions[2] / 2] )
                    cube( cameraBlockDimensions, center = true);
                
                // Internal Void
                translate( [0, 0, -cameraVoidDimensions[2] / 2] )
                    cube( [cameraVoidDimensions[0], cameraVoidDimensions[1] + clearancePiY * 2, cameraVoidDimensions[2] + manifoldCorrection], center = true);
            }
            

            
            // Mount Extension Block
            translate( [0, cameraMountInnerDiameter/2 + mountExtensionOuter[1]/2, -cameraBlockDimensions[2] - mountExtensionOuter[2]/2] )
                cube( [mountExtensionOuter[0], mountExtensionOuter[1], mountExtensionOuter[2]], center = true);
            translate( [0, -cameraMountInnerDiameter/2 - mountExtensionOuter[1]/2, -cameraBlockDimensions[2] - mountExtensionOuter[2]/2] )
                cube( [mountExtensionOuter[0], mountExtensionOuter[1], mountExtensionOuter[2]], center = true);

            // Mount Shroud
            translate( [0, 0, -cameraBlockDimensions[2] - cameraMountDepth] )
            {
                difference()
                {
                    // Shroud
                    donut(cameraMountOuterDiameter, cameraMountInnerDiameter, cameraMountDepth);
            
                    // Rotation Indents
                    for ( r = [0, 180] )
                        rotate( [0, 0, r] )
                            translate( [cameraMountOuterDiameter/2, 0, cameraMountDepth/2] )
                                cube( [cameraRotationIndentXY[0], cameraRotationIndentXY[1], cameraMountDepth + manifoldCorrection * 2], center = true );
                }
                // Hole Reinforcement
                for ( r = [45, 135, 225, 315] )
                    rotate( [0, 0, r] )
                        translate( [cameraHoleReinforcementDistance, 0, cameraMountDepth/2] )
                        {
                            translate( [-cameraHoleReinforcementDia/2, 0, 0] )
                                cube( [cameraHoleReinforcementDia, cameraHoleReinforcementDia, cameraMountDepth], center = true);
                            cylinder(d=cameraHoleReinforcementDia, h=cameraMountDepth, center = true);
                        }
            }
            
        }    

        // Rotation indent for extension block
       translate( [0, 0, -cameraBlockDimensions[2] - cameraMountDepth] )
       {
            rotate( [0, 0, 90] )
                translate( [cameraMountInnerDiameter/2 + mountExtensionOuter[1], 0, cameraMountDepth/2] )
                    cube( [cameraRotationIndentXY[0], cameraRotationIndentXY[1], cameraMountDepth + manifoldCorrection * 2], center = true );
            rotate( [0, 0, 270] )
                translate( [cameraMountInnerDiameter/2 + mountExtensionOuter[1], 0, cameraMountDepth/2] )
                    cube( [cameraRotationIndentXY[0], cameraRotationIndentXY[1], cameraMountDepth + manifoldCorrection * 2], center = true );
       }


        // Mount extension Voids
        translate( [0, cameraMountInnerDiameter/2 + mountExtensionInner[1]/2 - mountExtensionToInside/2, -cameraBlockDimensions[2] - mountExtensionInner[2]/2 + cameraTopCaseThickness/2] )
            cube( [mountExtensionInner[0], mountExtensionInner[1] + mountExtensionToInside, mountExtensionInner[2] + cameraTopCaseThickness], center = true);
        translate( [0, -cameraMountInnerDiameter/2 - (mountExtensionInner[1]/2 - mountExtensionToInside/2), -cameraBlockDimensions[2] - mountExtensionInner[2]/2 + cameraTopCaseThickness/2] )
            cube( [mountExtensionInner[0], mountExtensionInner[1] + mountExtensionToInside, mountExtensionInner[2] + cameraTopCaseThickness], center = true);

        // Camera mounting holes
        for ( pos = [
            [cameraBoltHoleOffset,   cameraBoltHoleOffset],
            [-cameraBoltHoleOffset,  cameraBoltHoleOffset],
            [cameraBoltHoleOffset,  -cameraBoltHoleOffset],
            [-cameraBoltHoleOffset, -cameraBoltHoleOffset],
        ] )
            translate( [pos[0], pos[1], -(cameraBlockDimensions[2] + cameraMountDepth) - manifoldCorrection] )
                cylinder(d=boltHoleDiameter, h=cameraBlockDimensions[2] + cameraMountDepth + manifoldCorrection * 2);


        // Bolt Holes
        for ( pos = [
            [cameraBoltHoleOffset,   cameraBoltHoleOffset, 15],
            [-cameraBoltHoleOffset,  cameraBoltHoleOffset, -15],
            [cameraBoltHoleOffset,  -cameraBoltHoleOffset, -15],
            [-cameraBoltHoleOffset, -cameraBoltHoleOffset, 15],
            ] )
            translate( [pos[0], pos[1], -(cameraBlockDimensions[2] + cameraMountDepth) - manifoldCorrection] )
            {
                cylinder(d=boltHeadDiameter, h=cameraBoltHoleDepth + manifoldCorrection);
                translate( [0, 0, cameraBoltHoleDepth] )
                    cylinder(d1=boltHeadDiameter, d2=boltHoleDiameter, h=boltHeadHeight);
            }
  
        // Suction release channels
        translate( [-(cameraBlockDimensions[0] - cameraVentDimensions[0])/2, 0, 0] )
            suctionReleaseVent();
        translate( [(cameraBlockDimensions[0] - cameraVentDimensions[0])/2, 0, 0] )
            suctionReleaseVent();
            
        // Hole for camera mount
        translate( [0, 0, -cameraBlockDimensions[2] - cameraMountDepth - manifoldCorrection] )
           cylinder(d=cameraMountInnerDiameter, h=cameraBlockDimensions[2] + cameraMountDepth + manifoldCorrection * 2);
  
        // To check hole geometry
        //translate( [-20, -35, -40] )
        //   cube( [20, 20, 40] );
    }

    // Support to prevent warping, remove after printing
    /*
    translate( [0, 0, -cameraVoidDimensions[2]/2] )
        cube( [cameraVoidDimensions[0], cameraVoidSupportThickness, cameraVoidDimensions[2]], center = true );
    translate( [0, 0, -cameraVoidDimensions[2]/2] )
        cube( [cameraVoidSupportThickness, cameraVoidDimensions[1], cameraVoidDimensions[2]], center = true );
    */
}



module suctionReleaseVent()
{
    translate( [0, 0, -cameraVentDimensions[2]/2 + manifoldCorrection] )
        cube( [cameraVentDimensions[0] + manifoldCorrection * 2, cameraVentDimensions[1], cameraVentDimensions[2] + manifoldCorrection], center = true);
    translate( [0, 0, -cameraVentDimensions[2]] )
        rotate( [0, 90, 0] )
            cylinder(d=cameraVentTopDiameter, h=cameraVentDimensions[1] + manifoldCorrection * 2, center = true);
}
    


module piCaseTop()
{
    difference()
    {
        piCase(height = caseHeight, expandedBoltHole=true);
        
        translate( [0, 0, caseSplitHeight - caseHeight] )
            translate( [0, 0, caseHeight/2 - manifoldCorrection] )
                cube( [caseOuterBorder[0], caseOuterBorder[1], caseHeight + manifoldCorrection * 2], center = true);
        translate( [-piBoardDimensions[0]/2, -piBoardDimensions[1]/2, caseBottomTopThickness + caseBottomPiClearance] )
    raspberryPi4BModel();

    }
}



module piCaseBottom()
{
    difference()
    {
        piCase(height = caseHeight, expandedBoltHole=false);
        translate( [0, 0, caseSplitHeight] )
            translate( [0, 0, caseHeight/2 - manifoldCorrection] )
                cube( [caseOuterBorder[0], caseOuterBorder[1], caseHeight + manifoldCorrection * 2], center = true);
        translate( [-piBoardDimensions[0]/2, -piBoardDimensions[1]/2, caseBottomTopThickness + caseBottomPiClearance] )
    raspberryPi4BModel();
    }
       
    // SDCard slot support posts
    translate( sdCardSupportPos )

    for ( posY = piBoardSDCardSupportLocs )
    {
        translate( [0, posY, 0] )
            cylinder(d=piBoardSDCardSupportDiameter, h=caseSplitHeight);
    }
}


    
module piCase(height, expandedBoltHole)
{
    difference()
    {
        // Rounded case outer shape
        piCaseFilled(height);
        // Variables we need for the next calculation
        caseBoltHoleTemplate     = [caseOuterBorder[0] - caseBoltHoleInset * 2, caseOuterBorder[1] - caseBoltHoleInset * 2 + clearancePiY];
        caseBoltHoleTemplateHalf = caseBoltHoleTemplate / 2;

        // Holes to bolt case together
        for ( pos = [ 
            [caseBoltHoleTemplateHalf[0], caseBoltHoleTemplateHalf[1]],
            [-caseBoltHoleTemplateHalf[0], caseBoltHoleTemplateHalf[1]],
            [caseBoltHoleTemplateHalf[0], -caseBoltHoleTemplateHalf[1]],
            [-caseBoltHoleTemplateHalf[0], -caseBoltHoleTemplateHalf[1]],
            ])
        {
            translate( [pos[0], pos[1], 0] )
            {
                caseBoltHole(height, expandedBoltHole);
                translate( [0, 0, -manifoldCorrection] )
                    cylinder(d=nutDiameter, h=caseNutDepth + manifoldCorrection, $fn=6);
            }
        }
        
        // Void for the Pi and hats inside the case
        difference()
        {
            void = [piBoardDimensions[0] + clearancePiX * 2, piBoardDimensions[1] + clearancePiY * 2, caseBottomPiClearance + casePCBToTopHatHeight];
            translate( [0, 0, void[2]/2 + caseBottomTopThickness] )
                cube( void, center = true);
            
            //Mounting holes for pi
            translate( [-piBoardDimensions[0]/2, -piBoardDimensions[1]/2, caseBottomTopThickness] )
            {
                for ( pos = piBoardHoleLocation )
                {
                    translate( [pos[0], pos[1], 0] )
                        donut(caseBottomPiHoleOuterDia, boltHoleDiameter, caseBottomPiClearance); 
                }
            }
        }
        
        // Logo
        translate( [0, 0, height] )
        {
            if      ( logoNum == 1 ) logo1();                
            else if ( logoNum == 2 ) logo2();
            else if ( logoNum == 3 ) logo3();
            else    echo("Error: Unrecognized logoNum");
        }
            
        // Fan Vent
        translate( [fanCenterPosition[0], fanCenterPosition[1], height - caseBottomTopThickness] )
        {
            fanVent();
        }
        
        // Side Vents
        sideVentStrip(sideVent1[0], sideVent1[1], sideVent1[2], sideVentDiamondSpacing, caseSideThickness + manifoldCorrection * 2, sideVentDiamondSize);
        sideVentStrip(sideVent2[0], sideVent2[1], sideVent2[2], sideVentDiamondSpacing, caseSideThickness + manifoldCorrection * 2, sideVentDiamondSize);
        rotate( [0, 0, 90] )
            sideVentStrip(sideVent3[0], sideVent3[1], sideVent3[2], sideVentDiamondSpacing, caseSideThickness + manifoldCorrection * 2, sideVentDiamondSize);
        
        // Port Recesses
        rotate( [0, 0, 90] )
            translate( portRecess2Pos )
                cube(portRecess2Dimensions);
        rotate( [0, 0, 90] )
            translate( portRecess3Pos )
                cube(portRecess3Dimensions);

        rotate( [0, 0, -90] )
            translate( portRecess4Pos )
                cube(portRecess4Dimensions);
        
        // Camera Bolt Holes
        for ( pos = [
                [cameraBoltHoleOffset,   cameraBoltHoleOffset],
                [-cameraBoltHoleOffset,  cameraBoltHoleOffset],
                [cameraBoltHoleOffset,  -cameraBoltHoleOffset],
                [-cameraBoltHoleOffset, -cameraBoltHoleOffset],
            ] )
            translate( [pos[0], pos[1]] )
            {
                translate( [0, 0, -manifoldCorrection] )
                   cylinder(d=boltHoleDiameter, h=caseBottomTopThickness + manifoldCorrection * 2);
                translate( [0, 0, caseBottomTopThickness - cameraNutHoleDepth] )
                    cylinder(d=nutDiameter, h=cameraNutHoleDepth + manifoldCorrection, $fn=6);
 
                translate( [0, 0, -manifoldCorrection] )  
                    donut(cameraPostRecessDonut[0], cameraPostRecessDonut[1], cameraPostRecessDonut[2]);
            }
            
        // Camera cable hole
        translate( [0, caseCamCableHoleOffsetY, caseBottomTopThickness/2] )
            cube( [caseCamCableHoleDimensions[0], caseCamCableHoleDimensions[1], caseBottomTopThickness + manifoldCorrection * 2], center = true );
            
        //Mounting bolt holes pi
        translate( [-piBoardDimensions[0]/2, -piBoardDimensions[1]/2, 0] )
        {
            for ( pos = piBoardHoleLocation )
            {
                translate( [pos[0], pos[1], -manifoldCorrection] )
                {
                    cylinder(d=boltHoleDiameter, caseBottomTopThickness + manifoldCorrection * 2); 
                    cylinder(d1=boltHeadDiameter, d2=boltHoleDiameter, boltHeadHeight + manifoldCorrection);
                }
            }
        }

        // Hole for the external GPS Cable
        if ( externalGps )
        {
            translate( [(piBoardDimensions[0] + clearancePiX * 2)/2 + caseSideThickness/2, 0, height-gpsExternalCableZPosZ] )
                rotate( [0, 90, 0] )
                    cylinder(d=gpsExternalCableHoleDiameter, h=caseSideThickness + manifoldCorrection * 2, center = true);
        }
        
        // XVS Lead Channel
        translate( xvsLeadChannelPos )
            cube( xvsLeadChannelDimensions );
    }
    
    // Fan Posts and Clamps
    translate( [fanCenterPosition[0], fanCenterPosition[1], height - caseBottomTopThickness] )
    {
        rotate( [0, 180, 0] )
            fanPostsAndClamp();
    }
    
    
    // DC Jack Reinforcement
    translate( [-piBoardDimensions[0]/2, -piBoardDimensions[1]/2 - clearancePiY + timingBoardReinforcementThickness, caseBottomTopThickness] )
        translate( [timingBoardJackPos[0], timingBoardJackPos[1], 0] )
        {
            difference()
            {
                raspberryPiCubePort([timingBoardJackDimensions[0] + 5, timingBoardReinforcementThickness, caseBottomPiClearance + casePCBToTopHatHeight], 0);

                translate( [0, -timingBoardReinforcementThickness/2 + manifoldCorrection, 0] )
                    cube( [timingBoardJackDimensions[0] + 5 + manifoldCorrection * 2, timingBoardReinforcementThickness + manifoldCorrection, 30.9], center = true );
            }
        }
}



module fanPostsAndClamp()
{
    // Fan Posts
    for ( pos = [
        [fanHolePositionXY,   fanHolePositionXY],
        [-fanHolePositionXY,  fanHolePositionXY],
        [fanHolePositionXY,  -fanHolePositionXY],
        [-fanHolePositionXY, -fanHolePositionXY],
        ] )
    {
        translate( [pos[0], pos[1], 0] )
        {
           cylinder(d=fanPostDiameter, h=fanPostHeight);
        }
    }

    // Fan Clips
    translate( [0, -fanDimensions[1]/2 - fanClipThickness/2, 0] )
        clip(fanClipWidth, fanClipThickness, fanClipHeight, fanClipRoundThickness);
    translate( [0, fanDimensions[1]/2 + fanClipThickness/2, 0] )
        rotate( [0, 0, 180] )
            clip(fanClipWidth, fanClipThickness, fanClipHeight, fanClipRoundThickness);
}



module sideVentStrip(centerPos, length, height, spacing, thickness, size)
{
    for ( y = [centerPos[2] - height/2 : spacing : centerPos[2] + height/2 ] )
        for ( x = [centerPos[0] - length/2 : spacing : centerPos[0] + length/2] )
            translate( [x, centerPos[1], y] )
                rotate( [0, 45, 0] )
                    cube( [size, thickness, size], center = true);
}



module fanVent()
{
    hexagonSize = 3;
    hexagonBorder = 1.0;
    
    translate( [0, 0, -caseBottomTopThickness * 0.5] )
        intersection()
        {
            translate( [hexagonSize, 0, 0] )
            {
                delta = (sqrt(hexagonSize)/2) * hexagonSize;
        
                for ( y = [-delta * 6:delta:delta * 6] )
                    for ( x = [-hexagonSize * 1.5 * 5:hexagonSize*1.5:hexagonSize * 1.5 * 5] )
                        translate( [x, y, 0] )
                            cylinder(d=hexagonSize-hexagonBorder/2, h=caseBottomTopThickness * 2 + manifoldCorrection * 2, $fn=6);

                for ( y = [-delta * 6:delta:delta * 6] )
                    for ( x = [-hexagonSize * 1.5 * 5:hexagonSize * 1.5:hexagonSize * 1.5 * 5] )
                        translate( [x + hexagonSize * 1.5/2, y + delta*0.5, 0] )
                            cylinder(d=hexagonSize-hexagonBorder/2, h=caseBottomTopThickness * 2 + manifoldCorrection * 2, $fn=6);
            }
        
            cylinder(d=fanVentDiameter, h=caseBottomTopThickness * 2 + manifoldCorrection * 2);
        }
}



module caseBoltHole(height, expandedBoltHole)
{
    holeDiameter = (expandedBoltHole == true) ? boltHoleDiameter : boltHoleDiameter;
    
    translate( [0, 0, caseBottomTopThickness] )
    {
        cylinder(d=holeDiameter, h=caseBoltLength + manifoldCorrection);
        translate( [0, 0, caseBoltLength - boltHeadHeight] )
            cylinder(d1=holeDiameter, d2=boltHeadDiameter, h=boltHeadHeight);
        translate( [0, 0, caseBoltLength] )
            cylinder(d=boltHeadDiameter, h=height);
    }
}




module piCaseFilled(height)
{
    linear_extrude(height=height)
    {
        // Half dimensions to make drawing the polygon easier with +/- positions about a center
        cOuterBorder = caseOuterBorder / 2;
        cOuterInset  = caseOuterInset  / 2;

        // Anti-clockwise points drawing the outline
        radiiPoints=[
            [cOuterBorder[0],                       cOuterBorder[1],                        caseOuterBorderRadius],       
            [cOuterInset[0] - caseOuterInsetInset,  cOuterInset[1],                         caseOuterInsetRadius],   
            [-cOuterInset[0] + caseOuterInsetInset, cOuterInset[1],                         caseOuterInsetRadius],
            [-cOuterBorder[0],                      cOuterBorder[1],                        caseOuterBorderRadius],
            [-cOuterInset[0],                       cOuterInset[1] - caseOuterInsetInset,   caseOuterInsetRadius],    
            [-cOuterInset[0],                       -cOuterInset[1] + caseOuterInsetInset,  caseOuterInsetRadius], 
            [-cOuterBorder[0],                      -cOuterBorder[1],                       caseOuterBorderRadius],
            [-cOuterInset[0] + caseOuterInsetInset, -cOuterInset[1],                        caseOuterInsetRadius], 
            [cOuterInset[0] - caseOuterInsetInset,  -cOuterInset[1],                        caseOuterInsetRadius],
            [cOuterBorder[0],                       -cOuterBorder[1],                       caseOuterBorderRadius],
            [cOuterInset[0],                        -cOuterInset[1] + caseOuterInsetInset,  caseOuterInsetRadius], 
            [cOuterInset[0],                        cOuterInset[1] - caseOuterInsetInset,   caseOuterInsetRadius],    
            ];
    
        // Draw the rounded Polygon
        polygon(polyRound(radiiPoints,30));
    
        // Draw the unrounded polygon (use for testing, comment out otherwise
        //translate([0,0,0.3])polygon(getpoints(radiiPoints));//transparent copy of the polgon without rounding
    }
}



// Board original is bottom left
// Reference: https://static.cytron.io/image/catalog/products/RASPBERRY-PI-4B-1G/Raspberry%20Pi%204%20Model%20B%20Dimension.jpg

module raspberryPi4BModel()
{
    // PCB
    difference()
    {
        color( [0.0, 0.7, 0.0 ] )
            translate( [piBoardDimensions[0]/2, piBoardDimensions[1]/2, 0] )
                roundedRect(piBoardDimensions[0], piBoardDimensions[1], piBoardDimensions[2], piBoardDimensions[3]); 
        
        for ( pos = piBoardHoleLocation )
        {
            translate( [pos[0], pos[1], -manifoldCorrection] )
                cylinder(d=2.6, h=piBoardDimensions[2] + manifoldCorrection * 2);
        }
    }
    
    // SD Card Protusion
    color( [0, 0, 0] )
        translate( [0, piBoardDimensions[1]/2, piBoardSDCardSlotPosZ] )
            translate( [-piBoardSDCardSlotDimensions[0], -piBoardSDCardSlotDimensions[1]/2, -piBoardSDCardSlotDimensions[2]] )
                cube( piBoardSDCardSlotDimensions );
    
    translate( [ 0, 0, piBoardDimensions[2]] )
    {
        // Header
        color( [0, 0, 0] )
            translate( piBoardHeaderPos )
                cube( piBoardHeaderDimensions );
                
        // Timing Board 12V DC Jack
        color( [0.9, 0.9, 0.9] )
            translate( [timingBoardJackPos[0], timingBoardJackPos[1], timingBoardJackPos[2]] )
                raspberryPiCubePort(timingBoardJackDimensions, raspberryPiPortClearance);
                        
        // USB1        
        color( [0.9, 0.9, 0.9] )
            translate( [piBoardDimensions[0], piBoardUSB1Position, 0] )
                rotate( [0, 0, 90] )
                    raspberryPiCubePort(piBoardUSB1Dimensions, raspberryPiPortClearance);
                    
        // USB2        
        color( [0.9, 0.9, 0.9] )
            translate( [piBoardDimensions[0], piBoardUSB2Position, 0] )
                rotate( [0, 0, 90] )
                    raspberryPiCubePort(piBoardUSB2Dimensions, raspberryPiPortClearance);
                    
        // Ethernet        
        color( [0.9, 0.9, 0.9] )
            translate( [piBoardDimensions[0], piBoardEtherPosition, 0] )
                rotate( [0, 0, 90] )
                    raspberryPiCubePort(piBoardEtherDimensions, raspberryPiPortClearance);

        // LED1        
        color( [0.9, 0.9, 0.9] )
            translate( [-piBoardLED1Dimensions[1], piBoardLED1Position[0], piBoardLED1Position[1]] )
                rotate( [0, 0, 90] )
                    raspberryPiCubePort(piBoardLED1Dimensions, 0);

        // LED2        
        color( [0.9, 0.9, 0.9] )
            translate( [-piBoardLED2Dimensions[1], piBoardLED2Position[0], piBoardLED1Position[1]] )
                rotate( [0, 0, 90] )
                    raspberryPiCubePort(piBoardLED2Dimensions, 0);
    }
}



module raspberryPiCubePort(dimensions, clearance)
{
    translate( [-dimensions[0]/2 - clearance, -dimensions[1], -clearance] )
        cube( [dimensions[0] + clearance * 2, dimensions[1], dimensions[2] + clearance * 2] );
}



// Dimensions are [diameter, thickness]

module raspberryPiCylinderPort(dimensions, clearance)
{
    //translate( [-dimensions[0]/2 - clearance, -dimensions[1], -clearance] )
    translate( [0, 0, dimensions[0]/2] )
        rotate( [90, 0, 0] )
            cylinder(d=dimensions[0] + clearance * 2, h=dimensions[1]);
}



module roundedRect(width, length, height, radius)
{
    w = width - radius * 2;
    l = length - radius * 2;
 
    hull()
    {
        for ( pos = [
                [ w/2,  l/2],
                [-w/2,  l/2],
                [ w/2, -l/2],
                [-w/2, -l/2]
            ] )
        {   
            translate( [pos[0], pos[1], 0] )
                cylinder(r=radius, h=height);
        }
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