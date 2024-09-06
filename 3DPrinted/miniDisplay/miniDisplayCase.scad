// Needs:   3 x M2.5x14mm bolt
//          3 x M2.5 nuts
//
// FDM:
//      Print partNum 0
//      
//          Filament Color:  Main: ASA Green (closer to Turquoise)
//          Drying:          ASA will need drying before use, it comes from Bambu Labs too wet to print well.  
//                           12hrs should be enough at 70C (ASA setting on Creality)
//          AMS Compatible:  Yes (need to make sure descicant is dry in AMS)
//          Plate:           Smooth PEI Plate
//          Bed Temperature: 110C (yes, 10C over)
//          Bed Adhesion:    Bambu Liquid Glue
//          Support:         Yes   (** USE Tree(auto))
//          Infill:          15%
//
//      Print partNum 1
//      
//          Filament Color:  TPU 95A HF Yellow
//          Drying:          Dry as appropriate
//          AMS Compatible:  No
//          Plate:           Smooth PEI Plate
//          Bed Temperature: Regular
//          Bed Adhesion:    Bambu Liquid Glue
//          Support:         No
//          Infill:          15%
//
// Post Processing:
//      - Wash adhesive off parts
//      - Dry parts
//      - Remove white haze on cases where there was plate contact with heat gun

partNum                 = 0;    // 0 = Case (both parts), 1 = Buttons, 2 = Bottom Case, 3 = Top Case

splitCase               = true;
caseSideBorder          = 2.0;
caseBottomBorder        = 3.0;
caseTopBorder           = 1.0;
caseRadius              = 2.5;
caseInnerDimensions     = [52, 23.5, 10.5];
caseOuterDimensions     = caseInnerDimensions + [caseSideBorder * 2, caseSideBorder * 2, caseBottomBorder + caseTopBorder];

pcbBaseHeight           = 6.0;

caseSplitHeight         = caseBottomBorder + 4.4;

manifoldCorrection      = 0.01;
manifoldCorrection2     = manifoldCorrection * 2;

holeUsbCDimensions      = [caseSideBorder + manifoldCorrection * 2, 9.4, 3.6];
holeUsbCPos             = [-caseInnerDimensions[0]/2 + manifoldCorrection, 0, caseSplitHeight];

boltPostBottomDiameter  = 4.0;
boltPostTopDiameter     = 5.0;
boltPostXY              = [-caseInnerDimensions[0]/2 + 3.0, 17.8/2];

boardPostDiameter       = 3.0;
boardPostInsetDiameter  = 2.0;
boardPostXY             = [boltPostXY[0] + 45.5, 19/2.0];
pcbBoardClearance       = 0.05;
pcbBoardThickness       = 1.6;

ledHoleDiameter         = 1.5;
ledHolePosXY1           = [-caseInnerDimensions[0]/2 + 2.3, -5.0];
ledHolePosXY2           = [-caseInnerDimensions[0]/2 + 2.3, 5.0];
//ledHolePosXY3           = [-caseInnerDimensions[0]/2 + 29.6, 3.2];

lcdHoleDimensions       = [28.0, 17.2];
lcdHolePosXY            = [-caseInnerDimensions[0]/2 + 11.7, 0];

buttonHoleDimensions    = [5.0-0.8, 4.0];
buttonD0HolePosXY       = [-caseInnerDimensions[0]/2 + 8.0 + 0.4, -7.0];
buttonD1HolePosXY       = [-caseInnerDimensions[0]/2 + 8.0 + 0.4, 0.0];
buttonD2HolePosXY       = [-caseInnerDimensions[0]/2 + 8.0 + 0.4, 7.0];
buttonResetHolePosXY    = [-caseInnerDimensions[0]/2 + 45.0, 0.0];

boltDiameter            = 2.7 + 0.3;
boltHeadDiameter        = 4.9;
boltHeadHeight          = 1.7;
boltLength              = 14.0;
nutDiameter             = 5.9 + 0.3;
nutThickness            = 2.0;
headToNutLength         = 12.5;
boltReinforceDiameter   = 6.4;
boltReinforceHeight     = 2.0;

cubeDimXY               = [caseOuterDimensions[0] + manifoldCorrection * 2, caseOuterDimensions[0] + manifoldCorrection * 2];

loneBoltShroudDiameter  = 7.5;
loneBoltShroudPosXY     = [caseOuterDimensions[0] / 2 + loneBoltShroudDiameter/2, 0];

ventsXYRange            = [19, 10];
ventsDistance           = 2.5;
ventsDiameter           = 1.5;

buttonMainDimensions    = [buttonHoleDimensions[0] - 0.5, buttonHoleDimensions[1] - 0.5];
buttonMainHeight        = 2.8;
legLongWidth            = 0.8;
legLongLength           = buttonMainDimensions[0] + 0.3 + 2.0;
legShortWidth           = 1.5;
legShortLength          = buttonMainDimensions[1] + 0.3 + 2.0;
legThickness            = 0.5;
buttonLozenge           = [3.8, 3.0, 0.5];
buttonCornerDimensions  = [2.0, 2.0, 0.8];
    


$fn                     = 40;


if ( partNum == 0 )
{
    if ( splitCase )
    {
        splitCase(0);
        postsBottom();
        translate( [0, cubeDimXY[1]/2 + 3, caseSplitHeight + caseOuterDimensions[2] - caseSplitHeight] )
            rotate( [ 180, 0, 0] )
                postsTop();    
    }
    else
    {
        case();
        postsBottom();
        postsTop();
    }
}

if ( partNum == 1)
{
    translate( [0, cubeDimXY[1]/2 + 3, 0] )
        buttons();
}

if ( partNum == 0 || partNum == 2 )
{
    if ( splitCase )
    {
        splitCase(-1);
        postsBottom();  
    }
}

if ( partNum == 0 || partNum == 3 )
{
    if ( splitCase )
    {
        splitCase(1);
        translate( [0, cubeDimXY[1]/2 + 3, caseSplitHeight + caseOuterDimensions[2] - caseSplitHeight] )
            rotate( [ 180, 0, 0] )
                postsTop();    
    }
}



module buttons()
{    
    caseTopBorderOffset = caseOuterDimensions[2] - caseTopBorder - manifoldCorrection;
    
    buttonsSurroundThickness    = 0.4;
    buttonsSurroundExtra    = 5.5;
    buttonsBorderDimensions = [buttonResetHolePosXY[0] - buttonD0HolePosXY[0] + buttonMainDimensions[0], buttonD2HolePosXY[1] - buttonD0HolePosXY[1] + buttonMainDimensions[1] + buttonsSurroundExtra, buttonsSurroundThickness];
    borderInsetAmount   = 4.0;
    buttonBorderInsetDimensions = [buttonsBorderDimensions[0] - buttonMainDimensions[0] * 2, buttonsBorderDimensions[1] - borderInsetAmount, buttonsBorderDimensions[2] + manifoldCorrection2];

    difference()
    {
        union()
        {
            // button holes D0/D1/D2
            for ( posXY = [buttonD0HolePosXY, buttonD1HolePosXY, buttonD2HolePosXY] )
                translate( [posXY[0], posXY[1], 0] )
                    button();
        
            // button holes reset
            translate( [buttonResetHolePosXY[0], buttonResetHolePosXY[1], 0] )
                    rotate( [0, 0, 90] )
                        button();
                     
            translate( [buttonD0HolePosXY[0] - buttonMainDimensions[0]/2, -(buttonD2HolePosXY[1] - buttonD0HolePosXY[1])/2 - buttonMainDimensions[1]/2 - buttonsSurroundExtra/2, 0 ] )
                cube( [buttonsBorderDimensions[0], buttonsBorderDimensions[1], buttonsBorderDimensions[2]], center = false);
        }
        
        translate( [buttonD0HolePosXY[0] - buttonMainDimensions[0]/2, -(buttonD2HolePosXY[1] - buttonD0HolePosXY[1])/2 - buttonMainDimensions[1]/2 - buttonsSurroundExtra/2, -manifoldCorrection ] )
            translate( [buttonMainDimensions[0], borderInsetAmount/2, 0] )
                cube( buttonBorderInsetDimensions, center = false);
    }
}



module button()
{
    translate( [0, 0, buttonMainHeight/2] )
        cube( [buttonMainDimensions[0], buttonMainDimensions[1], buttonMainHeight], center = true);        
}



module splitCase(parts)
{
    cubeOriginXY = [-cubeDimXY[0] / 2, -cubeDimXY[1]/2];
    
    if ( parts == 0 || parts == 1 )
        translate( [0, cubeDimXY[1]/2 + 3, caseSplitHeight + caseOuterDimensions[2] - caseSplitHeight] )
            rotate( [ 180, 0, 0] )
                difference()
                {
                    case();
                    translate( [cubeOriginXY[0], cubeOriginXY[1], -manifoldCorrection] )
                        cube([cubeDimXY[0] * 2, cubeDimXY[1], caseSplitHeight + manifoldCorrection]);
                }
    
    if ( parts == 0 || parts == -1 )
        difference()
        {
            case();
            translate( [cubeOriginXY[0], cubeOriginXY[1], caseSplitHeight] )
                cube([cubeDimXY[0] * 2, cubeDimXY[1], caseOuterDimensions[2] - caseSplitHeight + manifoldCorrection]);
        }
}



module case()
{
    difference()
    {
        union()
        {
            roundedCube(caseOuterDimensions, caseRadius);
            translate( [loneBoltShroudPosXY[0], loneBoltShroudPosXY[1], 0] )
            {
                cylinder(d = loneBoltShroudDiameter, h = caseOuterDimensions[2]);
                translate( [-loneBoltShroudDiameter/4, 0, caseOuterDimensions[2]/2] )
                    cube( [loneBoltShroudDiameter/2, loneBoltShroudDiameter, caseOuterDimensions[2]], center = true );
            }
        }
        translate( [0, 0, caseBottomBorder] )
            roundedCube(caseInnerDimensions, caseRadius);
        
        // USB C Hole
        translate( holeUsbCPos )
            rotate( [90, 0, 270] )
                lozenge(holeUsbCDimensions[1], holeUsbCDimensions[2],holeUsbCDimensions[0]);

        // led holes
        //for ( posXY = [ledHolePosXY1, ledHolePosXY2, ledHolePosXY3] )
        for ( posXY = [ledHolePosXY1, ledHolePosXY2] )
            translate( [posXY[0], posXY[1], -manifoldCorrection] )
                cylinder(d = ledHoleDiameter, h = caseBottomBorder + manifoldCorrection * 2);

        caseTopBorderOffset = caseOuterDimensions[2] - caseTopBorder - manifoldCorrection;

        // lcd hole
        translate( [lcdHolePosXY[0], -lcdHoleDimensions[1]/2 + lcdHolePosXY[1], caseTopBorderOffset] )
            cube( [lcdHoleDimensions[0], lcdHoleDimensions[1], caseTopBorder + manifoldCorrection * 2] );
        
        // button holes D0/D1/D2
        for ( posXY = [buttonD0HolePosXY, buttonD1HolePosXY, buttonD2HolePosXY] )
            translate( [posXY[0], posXY[1], caseTopBorderOffset] )
                translate( [0, 0, caseTopBorder/2 + manifoldCorrection] )
                    cube( [buttonHoleDimensions[0], buttonHoleDimensions[1], caseTopBorder + manifoldCorrection * 2], center = true );
        
        // button holes reset
        translate( [buttonResetHolePosXY[0], buttonResetHolePosXY[1], caseTopBorderOffset] )
            translate( [0, 0, caseTopBorder/2 + manifoldCorrection] )
                rotate( [0, 0, 90] )
                    cube( [buttonHoleDimensions[0], buttonHoleDimensions[1], caseTopBorder + manifoldCorrection * 2], center = true ); 
        
        // Bolt Nut Holes
        translate( [boltPostXY[0], boltPostXY[1], 0] )
            boltNut();
        translate( [boltPostXY[0], -boltPostXY[1], 0] )
            boltNut();
        
        // Lone Bot nut Holes
        translate( [loneBoltShroudPosXY[0], loneBoltShroudPosXY[1], 0] )
            boltNut();
        
        // Vent Holes
        translate( [0, 0, -manifoldCorrection] )
            for ( x = [-ventsXYRange[0]:ventsDistance:ventsXYRange[0]] )
                for ( y = [-ventsXYRange[1]:ventsDistance:ventsXYRange[1]] )
                    translate( [x, y, 0] )
                        cylinder(d=ventsDiameter, h = caseBottomBorder + manifoldCorrection * 2, $fn=6);
    }
}



module boltNut()
{
    translate( [0, 0, caseOuterDimensions[2]] )
        rotate( [180, 0, 0] )
        {
            cylinder(d1 = boltHeadDiameter, d2 = boltDiameter, h = boltHeadHeight);
            translate( [0, 0, -boltHeadHeight + manifoldCorrection] )
                cylinder(d = boltHeadDiameter, h = boltHeadHeight);
            translate( [0, 0, 0] )
                cylinder(d = boltDiameter, h = boltLength);
            translate( [0, 0, boltHeadHeight + headToNutLength - nutThickness] )
                cylinder(d = nutDiameter, h = nutThickness * 4, $fn = 6);
        }
}



module postsBottom()
{   
    topPostHeight = caseInnerDimensions[2] - (pcbBaseHeight + pcbBoardThickness + pcbBoardClearance);
    
    translate( [0, 0, caseBottomBorder] )
    {
        // Bolt Posts
        for ( posY = [-boltPostXY[1], boltPostXY[1]] )
            translate( [boltPostXY[0], posY, 0] )
            {
                donut(boltReinforceDiameter, boltDiameter, boltReinforceHeight);
                donut(boltPostBottomDiameter, boltDiameter, pcbBaseHeight);
            }
        
        // Board Posts
        for ( posY = [-boardPostXY[1], boardPostXY[1]] )
            translate( [boardPostXY[0], posY, 0] )
            {
                cylinder(d = boardPostDiameter, pcbBaseHeight);
                translate( [0, 0, pcbBaseHeight] )
                    cylinder(d = boardPostInsetDiameter, pcbBoardThickness);
            }        
    }
}



module postsTop()
{   
    topPostHeight = caseInnerDimensions[2] - (pcbBaseHeight + pcbBoardThickness + pcbBoardClearance);
        
    translate( [0, 0, caseBottomBorder] )
    {
        // Bolt Posts
        for ( posY = [-boltPostXY[1], boltPostXY[1]] )
            translate( [boltPostXY[0], posY, 0] )
            {
                translate( [0, 0, caseInnerDimensions[2] - topPostHeight] )
                {
                    difference()
                    {
                        donut(boltPostTopDiameter, boltDiameter, topPostHeight); 
                        translate( [0, 0, topPostHeight + caseTopBorder - boltHeadHeight] )
                            cylinder(d2 = boltHeadDiameter, d1 = boltDiameter, h = boltHeadHeight);
                    }   
                }
            }
        
        // Board Posts
        for ( posY = [-boardPostXY[1], boardPostXY[1]] )
            translate( [boardPostXY[0], posY, 0] )
            {
                translate( [0, 0, caseInnerDimensions[2] - topPostHeight] )
                    cylinder(d = boardPostDiameter, topPostHeight);
            }        
    }
}



module roundedCube(dimensions, radius)
{
    xCenter = dimensions[0] / 2 - radius;
    yCenter = dimensions[1] / 2 - radius;
    
    hull()
    {
        for (pos = [[-xCenter, -yCenter], [xCenter, -yCenter], [-xCenter, yCenter], [xCenter, yCenter]])
        {
            translate( [pos[0], pos[1], 0] )
                cylinder( r = radius, h = dimensions[2] );
        }
    }
}



module lozenge(width, height, thickness)
{
    origin = (width - height)/2;
    
    hull()
    {
        translate( [-origin, 0, 0] )
            cylinder(d = height, h = thickness);

        translate( [origin, 0, 0] )
            cylinder(d = height, h = thickness);
    }
}



module donut(outerDiameter, innerDiameter, height)
{
    difference()
    {
        cylinder(d = outerDiameter, h = height);
        translate( [0, 0, -manifoldCorrection] )
            cylinder(d = innerDiameter, h = height + manifoldCorrection * 2);
    }
}