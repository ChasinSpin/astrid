innerDiameter       = 31.6;
height              = 8;
thickness           = 1.5;
manifoldCorrection  = 0.01;


$fn = 80;

rotate( [0, 180, 0] )
    difference()
    {
        cylinder(d=innerDiameter + thickness * 2, h = height + thickness);
        translate( [0, 0, -manifoldCorrection] )
            cylinder(d=innerDiameter, h = height);
    }