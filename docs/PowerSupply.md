# Power Supply

Astrid with the OTEStamper board should be powered via the 12-15 Volt 2.1x5.5mm DC Input Jack on the OTEStamper board, which is common on astronomy equipment. This input jack is "center positive" and has a self-resettable 2A polyfuse.  Power to the input jack is reverse polarity protected. 

Supply voltages outside of this range will likely damage the board, the Raspberry Pi and may corrupt the SD Card.  We recommend against using 12V Cigarette lighter type connectors, as they often disconnect easily and can lead to SD Card corruption when that happens.

5.1-5.2VDC is generated internally by the OTEStamper board for the Raspberry Pi to run.  Please make sure that any wiring and the connector you use to supply Astrid can handle at least 2A. For reasonable run length, this means 16AWG or thicker for the wire, and likely 14AWG if you're supplying a larger mount too.

# Batteries

Field deployments will typically need a battery, here are our suggestions.  We recommend against using 12V battery power banks that have poor regulation or may not be able to handle the current.

Be sure to use the correct charger for the battery or power pack to avoid damage and fuse if using a battery directly.  Ensure the wiring used is large enough to handle the current required to avoid overheating, insulation melting and voltage drops.

LiFePO4 (Lithium Phosphate) battery chemistry is recommended for safety, cold weather performance, and battery longevity.  You should also verify that the battery has a BMC (Battery Management Controller) on board.

We particularly like the batteries made by Dakota and we own a few due to the exceptional cold-weather performance and warranty. 

Avoid the TalentCell and other power banks other than the ones listed below, often they have mediocre batteries and converters that can't keep up with the current / voltage required by Astrid and aren't the specifications they list.

If traveling by air with Lithium batteries, be aware that there are regulations depending on the size of the battery, and you should verify with your airline before travel.

For example, the [TSA guidelines](https://www.tsa.gov/travel/security-screening/whatcanibring/all?combine=batteries&page=1#:~:text=Lithium%20batteries%20with%20100%20watt%20hours%20or%20less%20in%20a%20device&text=Spare%20(uninstalled)%20lithium%20ion%20and,in%20carry%2Don%20baggage%20only)

**Runtimes are approximate.  "Runtime" means Astrid alone (typically tripod mount).  "Runtime with Mount" assumes a mid sized mount (EQ5/AM5) with a current draw of ~1Amp.**

| Battery | Capacity | Tested | Runtime (hrs) | Runtime With Mount (hrs) | Meets FAA Carry On Regulations | Comments |
| --- | --- | --- | --- | --- | --- | --- |
| [8 Energizer L91 Lithium AA](https://data.energizer.com/pdfs/l91.pdf) | 36Wh | No | 5-6 | Not feasable | Yes | Buy  at destination. Good to -15C, lower with less runtime. |
| [Dakota 12V 7Ah](https://dakotalithium.com/product/dakota-lithium-12v-7ah-battery-69/) | 84Wh | No | 12-14 | 3.5-4.5 | Yes | |
| [Celestron PowerTank Lithium (18771)](https://www.celestron.com/products/powertank-lithium) | 84Wh | No | 12-14 | 3.5-4.5 | Yes | Expensive |
| [Dakota 12V 10Ah](https://dakotalithium.com/product/dakota-lithium-12v-10ah-battery/) | 120Wh | No | 17-20 | 5-6.5 | Yes | |
| Sealed Lead Acid Battery | 120Wh | No | 14-17 | 4.5-5.5 | No | Heavy |
| [Celestron PowerTank Lithium Pro (18768)](https://www.celestron.com/products/powertank-lithium-pro) | 158Wh | No | 23-26 | 7-8.5 | Yes | Expensive |
| [Dakota 12V 18Ah](https://dakotalithium.com/product/dakota-lithium-12v-12ah-18-amp-hour-lifepo4-iron-phosphate-battery/) | 216Wh | Yes | 32-36 | 10-12 | No | |
| [Dakota 12V 54Ah](https://dakotalithium.com/product/dakota-lithium-12v-12ah-18-amp-hour-lifepo4-iron-phosphate-battery/) | 691Wh | Yes |90-100 | 30-34 | No | Expensive |
