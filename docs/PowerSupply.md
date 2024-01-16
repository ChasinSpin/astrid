# Power Supply

Astrid with the OTEStamper board should be powered via the 12-15 Volt 2.1x5.5mm DC Input Jack on the OTEStamper board, which is common on astronomy equipment. This input jack is "center positive" and has a self-resettable 2A polyfuse.  Power to the input jack is reverse polarity protected. 

Supply voltages outside of this range will likely damage the board and the Raspberry Pi and may corrupt the SD Card.  We recommend against using 12V Cigarette lighter-type connectors, as they often disconnect easily and can lead to SD Card corruption when that happens.

5.1-5.2VDC is generated internally by the OTEStamper board for the Raspberry Pi to run.  Please make sure that any wiring and the connector you use to supply Astrid can handle at least 2A. For reasonable run length, this means 16AWG or thicker for the wire, and likely 14AWG if you're supplying a larger mount too.

# Power Banks / Power Packs

__Power Banks / Power Packs are NOT Batteries__

__IMPORTANT:__ It's strongly suggested to avoid Power Banks or Power Packs for powering Astrid.  Power Banks / Power Packs (e.g. TalentCell) are most often made from cheap batteries with substandard electronics that are incapable of supplying regulated power to Astrid. This also applies to powering Astronomy Equipment in general (Mini PCs, Astro Cameras, Mounts, etc.).

Common problems with Power Banks/Power Packs are:

* Misrepresented Battery Capacity (specified at 3.7V not 12V)
* Power outputs auto switch off with low power drain, removing power from Astrid
* Low and/or varying voltage due to current limiting, poor boost conversion
* Fire risk/explosion risk
* Insufficient size

__Any Power Bank/Power Pack that contains Lithium Ion or Lithium Polymer batteries can also cause fires and can explode.  Lithium fires often can't be put out with water or chemical fire extinguishers.__

Examples:

* [https://www.youtube.com/watch?v=8nz5ijXcckI
](https://www.youtube.com/watch?v=8nz5ijXcckI)
* [https://m.youtube.com/watch?v=jq_0X1lStbo](https://m.youtube.com/watch?v=2hGfCwPwCPQ)
* [https://m.youtube.com/watch?v=2hGfCwPwCPQ](https://m.youtube.com/watch?v=2hGfCwPwCPQ)

There is no support/assistance available for Astrid setups using Power Banks / Power Banks if the problem is suggestive of being related to power issues.

Also, any larger power bank/power packs that have a 120V inverter are often square wave and not the correct sine wave output.  This can permanently damage any device plugged into it (such as a laptop power supply, or 12V DC power adapter).

Using LiFePO4 (Lithium Phosphate) 12V batteries instead is safer, significantly cheaper, and works (see below).

_There is one exception to this recommendation, and that is the Celestron Lithium and Lithium Pro LiFePO4 power banks(only), which are designed for astronomy applications.  However, as of now, these are untested with Astrid and they are significantly more expensive than an equivalent battery.  If you use one and it is working without power dropouts, please inform us._

# Household Power

Astrid can be powered at home with a 4A or greater 12V DC regulated center positive good quality power supply, for example:

* [https://agenaastro.com/zwo-12v-dc-adapter-for-cooled-camera-us.html](https://agenaastro.com/zwo-12v-dc-adapter-for-cooled-camera-us.html)
* [https://www.amazon.com/ALITOVE-Adapter-Converter-100-240V-5-5x2-1mm/dp/B01GEA8PQA](https://www.amazon.com/ALITOVE-Adapter-Converter-100-240V-5-5x2-1mm/dp/B01GEA8PQA)

# Batteries

Field deployments will typically need a battery, here are our suggestions. We use a 10Ah Dakota LiFePO4 12V battery.

Be sure to use the correct charger for the battery or power pack recommended by the manufacturer to avoid damage and fuse with a 5A fuse.  Ensure the wiring used is large enough to handle the current required to avoid overheating, insulation melting, and voltage drops.

LiFePO4 (Lithium Phosphate) battery chemistry is recommended for safety, cold weather performance, and battery longevity.  You should also verify that the battery has a BMC (Battery Management Controller) on board.  Lithium Ion and Lithium Polymer batteries should be avoided due to safety concerns, fire risk/explosion.

We particularly like the batteries made by Dakota, and we own a few due to their exceptional cold-weather performance and warranty. 

If traveling by air with lithium batteries, be aware that there are regulations depending on the size of the battery, and you should verify with your airline before traveling.

For example, the [TSA guidelines](https://www.tsa.gov/travel/security-screening/whatcanibring/all?combine=batteries&page=1#:~:text=Lithium%20batteries%20with%20100%20watt%20hours%20or%20less%20in%20a%20device&text=Spare%20(uninstalled)%20lithium%20ion%20and,in%20carry%2Don%20baggage%20only)

**Runtimes are approximate.  "Runtime" means Astrid alone (typically tripod mount).  "Runtime with Mount" assumes a mid-sized mount (EQ5/AM5) with a current draw of ~1Amp.**

| Battery | Capacity | Tested | Runtime (hrs) | Runtime With Mount (hrs) | Meets FAA Carry On Regulations | Comments |
| --- | --- | --- | --- | --- | --- | --- |
| [Dakota 12V 7Ah](https://dakotalithium.com/product/dakota-lithium-12v-7ah-battery-69/) | 84Wh | No | 12-14 | 3.5-4.5 | Yes | |
| [Dakota 12V 10Ah](https://dakotalithium.com/product/dakota-lithium-12v-10ah-battery/) | 120Wh | Yes | 17-20 | 5-6.5 | Yes | |
| [Dakota 12V 18Ah](https://dakotalithium.com/product/dakota-lithium-12v-12ah-18-amp-hour-lifepo4-iron-phosphate-battery/) | 216Wh | Yes | 32-36 | 10-12 | No | |
| [Dakota 12V 54Ah](https://dakotalithium.com/product/dakota-lithium-12v-12ah-18-amp-hour-lifepo4-iron-phosphate-battery/) | 691Wh | Yes |90-100 | 30-34 | No | Expensive |
| Sealed Lead Acid Gel Battery | 120Wh | No | 14-17 | 4.5-5.5 | No | Heavy |
| [Celestron PowerTank Lithium (18771)](https://www.celestron.com/products/powertank-lithium) | 84Wh | No | 12-14 | 3.5-4.5 | Yes | Expensive |
| [Celestron PowerTank Lithium Pro (18768)](https://www.celestron.com/products/powertank-lithium-pro) | 158Wh | No | 23-26 | 7-8.5 | Yes | Expensive |
| [8 Energizer L91 Lithium AA](https://data.energizer.com/pdfs/l91.pdf) | 36Wh | No | 5-6 | Not feasable | Yes | Buy  at destination. Good to -15C, lower with less runtime. Batteries are expensive and require a solder lug battery holder as most battery holders have small gauge wiring. A small lithium battery you can carry on a plane (e.g., the 10Ah Dakota listed above) is often the most cost-effective option if used more than once. |

# Power Connectors

The recommended way to connect a smaller LiFePO4 battery to Astrid is via a 5A Fuse and DC 5.5mm x 2.1mm male barrel plug with 16 Gauge (or thicker wiring).  The fuse is there to protect the battery from accidental touching of the barrel plug to a battery terminal.  

Often people will make their own power connectors or have connectors already available to them.  Here are some suggestions if you prefer to purchase an a mostly assembled connector without soldering / heat shrinking (you'll still need to crimp 2 terminals):

## Parts

* [Fused 5.5 x 2.1mm Jack](https://www.amazon.com/GELRHONR-Extension-Adapter-Security-Pedal-50cm/dp/B0BWRKRR6V)
* [2.1mm Extension](https://www.amazon.com/SIOCEN-Security-Extension-Surveillance-Standalone/dp/B07Y7XTBF7) 
* [5A Fuses](https://www.amazon.com/Fuses-Blade-Style-Circuit-Protection/dp/B07X313Q4T)
* [Quick Disconnect Terminal 0.25"](https://www.amazon.com/AIRIC-Insulated-Connector-Disconnect-Terminal/dp/B06XCWHY1B)

## Cable Construction

* Cut off the barrel socket close to the end of the socket (leaving just the 2.1mm plug that goes into Astrid.  Split wire and crimp on 2 x 0.25" quick disconnect terminals to connect to the battery (do not connect to battery yet)
* Plug in 2.1mm extension lead
* Replace fuse in the lead with the 5 Amp Fuse
