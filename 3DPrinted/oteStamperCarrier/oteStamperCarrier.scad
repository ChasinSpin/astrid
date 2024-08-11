// Overture PETG White, Engineering Plate 90C, Liquid Glue, 15% Fill

width                   = 58;
depth                   = 49;
postPositions           = [
            
                            [-width/2, -depth/2],
                            [-width/2, depth/2],
                            [width/2,  -depth/2],
                            [width/2,  depth/2]
                          ];
postOuterDiameter       = 6.0;
postInnerDiameter       = 2.5;
postInnerHeight         = 5.0;
postHeight              = 9.0;
postInterBoardHeight    = 15.0;
innerPostClearance      = 0.25;

plateWidth              = 65;
plateDepth              = 56;
plateThickness          = 1.0;


manifoldCorrection      = 0.01;
manifoldCorrection2     = manifoldCorrection * 2;

pcbDimensions           = [ 65.25, 56.25, 1.62];

$fn                     = 40;



bottomPlate();
translate( [plateWidth + 5, 0, 0 ] )
    topPlate();
for ( y = [0:8:16] )
{
    for ( x = [-26:8:80] )
        translate( [x, y + plateDepth/2 + 7, 0] )
            post(postInterBoardHeight);
    for ( x = [88:8:96] )
        translate( [x, y + plateDepth/2 + 7, 0] )
            post(postHeight);
}



module bottomPlate()
{
    translate( [0, 0, plateThickness / 2] )
        cube( [plateWidth, plateDepth, plateThickness], center = true );
    for ( pos = postPositions )
    {
        translate( [pos[0], pos[1], plateThickness] )
            post(postHeight);
    }
}


module topPlate()
{   
    difference()
    {
        union()
        {
            translate( [0, 0, plateThickness / 2] )
                cube( [plateWidth, plateDepth, plateThickness], center = true );
            for ( pos = postPositions )
            {
                translate( [pos[0], pos[1], 0] )
                    cylinder( d = postOuterDiameter, h = postHeight );
            }
        }
 
        for ( pos = postPositions )
        {
            translate( [pos[0], pos[1], -manifoldCorrection] )
                cylinder( d = postInnerDiameter + innerPostClearance, h = postHeight + manifoldCorrection2 );
        }
    }
}



module post(height)
{
    difference()
    {
        union()
        {
            cylinder( d = postOuterDiameter, h = height );
            translate( [0, 0, height] )
                cylinder( d = postInnerDiameter, h = postInnerHeight);
        }
        
        translate( [0, 0, -manifoldCorrection] )
            cylinder( d = postInnerDiameter + innerPostClearance, h = postInnerHeight + manifoldCorrection);
    }
}