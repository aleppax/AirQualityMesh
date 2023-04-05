## PCB
 
![mainboard rendering](https://github.com/aleppax/outdoorPMstation/blob/base/casing/fatherboard_oPMs.jpg "mainboard")

The PCB design is single sided, has no SMD parts and a minimalistic BOM. Components are on the opposite side of the copper layer. 
Hence it is very straightforward to make it at home both with a CNC or chemicals. 
The main purpose of the PCB is to speed up the assembly but it is better to choose 
terminals that guarantee contact continuity over time since this is an outdoor application partially exposed to weather conditions.
The two resistors are 20K and 30K Ohm, they are used as an external voltage divider to measure the battery voltage. 
We decided to avoid using the internal ADC3 with its own voltage divider because this relies on the WL_GPIO2 of the wireless chip and we didn't want conflicts during wifi communication. If a good precision isn't paramount it is possible to stop using the external circuit in favor of the builtin one.

The connection PCB has been designed so that half of the Raspberry Pico, the part where the antenna is located, protrudes, so as to move connection wires and tracks away as far as possible from the transceiver area.

## Case

![front view](https://github.com/aleppax/outdoorPMstation/blob/base/casing/pictures/case_1.jpeg "case front view")
![battery view](https://github.com/aleppax/outdoorPMstation/blob/base/casing/pictures/case_3.jpeg "4V battery inside")

the casing is designed to be composed mainly of cheap parts available from electrical component suppliers, for which a compact junction box was chosen (150 X 110 X 70 mm, IP 56), commercially available air vents (to which a double layer of mosquito netting was added for greater protection from small insects). Each air vent has an overall opening of 8 cm^2.

## Solar panel

![rear view](https://github.com/aleppax/outdoorPMstation/blob/base/casing/pictures/case_4.jpeg "case rear view")

The solar panel (Cellevia CL-SM3P) is extremely cheap but still slightly oversized, it has the secondary function of protecting the casing from direct solar radiation and has an aluminum frame for easier fixing.

## Fixing 

A sturdy joint plate with screws and nuts for fixing to a post or railing or fence. Different fixing systems will have to be studied according to the location.

## Sensor holder

The only customized component is the sensor fixing structure which allows to house two particulate sensors and possibly a humidity and temperature sensor. Subsequent redesigns could accommodate a small fan in case it is necessary to force a greater air exchange.

![mainboard rendering](https://github.com/aleppax/outdoorPMstation/blob/base/casing/sensor_tunnel.jpg "sensor tunnel")
![interior](https://github.com/aleppax/outdoorPMstation/blob/base/casing/pictures/case_interior.jpeg "case interior view")
![assembly](https://github.com/aleppax/outdoorPMstation/blob/base/casing/pictures/case_2.jpeg "3D printing the sensor holder")

