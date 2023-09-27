Version 0.9b: Initial

Version 0.9c: No electrical changes No electrical changes. Moved label for D1 below diode and clarified
orientation for the Buck Regulator to make it less like to assemble wrong way round.

TODO:

1. Increase buck regulator output by 0.05V as output range is 5.08 to 5.15 due to tolerances.

2. Maybe look at switching out back protection FET to one with lower RDS as drop across is large at high currents (buck can keep up fine)

3. Put HOT labels around buck converter and back protection FET

4. Change 5V fan to 12V fan/fet (maybe), possible overvoltage, and can you get a 12V small fan?

5. Add 100uF capacitor after reverse polarity fet to prevent surge damaging buck regulator


PSU CHARACTERISATION:

1. Voltage range is 7.5 - 18V, specified range to the user is 12V-15V @ 4A

2. Voltage dropout occurs at 7.5V

3. Buck starts to current limit (switch the PSU on and off) at 4.1A

4. Max temperature ofr the bucks convert (4A @ 18V) is 130C

5. Damage to the buck convert will occur at 20V

6. Fuse never gets triggered during normal use.  Would only get trigger if there
was failure on the board itself.


| PSU Output | Supply Input | Temperature |
| ---------- | ------------ | ----------- |
| 0.2A @ 5.04V | 0.062A @ 18V | Room |
| 1A @ 5.02V | 0.304A @ 18V | 42C |
| 2A @ 4.97V | 0.604A @ 18V | 57C |
| 3A @ 4.89V | 0.920A @ 18V | 85C |
| 4A @ 4.79V | 1.243A @ 18V | 125V |
