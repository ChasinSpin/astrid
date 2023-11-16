// Copyright: ChasinSpin, 2023
// License: MIT License

// Print 15% Fill No Support


plateBorderThickness            = 4;
plateBorderHeightShort          = plateBorderThickness + 10;
plateBorderHeightTall           = plateBorderHeightShort + 20;
plateBorderHeightExtra          = 20;
batteryCoverPlateDimensions     = [65, 68, 3];

velcroBlock                     = [45, 30, plateBorderHeightShort];

manifoldCorrection              = 0.01;

cableChannel                    = [plateBorderThickness + manifoldCorrection * 2, 7, 5];



batteryCover();



module batteryCover()
{
    difference()
    {
        batteryCover2();
        
        translate( [-batteryCoverPlateDimensions[0]/2 - plateBorderThickness/2, 0, plateBorderHeightShort - cableChannel[2]/2 + manifoldCorrection] )
            cube( cableChannel, center = true);
    }
}



module batteryCover2()
{
    translate( [0, 0, batteryCoverPlateDimensions[2] / 2] )
        cube(batteryCoverPlateDimensions, center = true);
    
        sideX(1.0, batteryCoverPlateDimensions[1] + plateBorderThickness*2, plateBorderHeightTall);
        sideX(-1.0, batteryCoverPlateDimensions[1] + plateBorderThickness*2, plateBorderHeightShort);
        sideY(1.0, batteryCoverPlateDimensions[0], plateBorderHeightTall);
        sideY(-1.0, batteryCoverPlateDimensions[0], plateBorderHeightTall);
   
   translate( [batteryCoverPlateDimensions[0] / 2 - velcroBlock[0]/2, 0, velcroBlock[2]/2] )
        cube( velcroBlock, center = true ); 
}


module sideY(plusMinus, length, height)
{
    translate( [0, 0, height/2] )
        translate( [0, plusMinus * ((plateBorderThickness + batteryCoverPlateDimensions[1])/2), 0] )
            cube([length, plateBorderThickness, height], center = true);
}


module sideX(plusMinus, length, height)
{
    translate( [0, 0, height/2] )
        translate( [plusMinus * ((plateBorderThickness + batteryCoverPlateDimensions[0])/2), 0, 0] )
            cube([plateBorderThickness, length, height], center = true);
}