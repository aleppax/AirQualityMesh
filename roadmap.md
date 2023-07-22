# Roadmap

## Early Proof of Concept

we are investigating many possibilities and the purpose of this stage is to define a roadmap for the Proof of Concept

## Proof of Concept -CURRENT-

At this stage the project is emerging from a glowing cauldron, nothing is permanent and the overall structure of the system is in progress.
We are currently evaluating:
 - [x] WiFi network, data queue, main routine
 - [x] acting as an Access Point and web server to configure the SSID and password from the user (unsecured) and other settings 
 - [x] MQTT connection,REST API
 - [ ] selection of parameters and launch of side projects: humidity, temperature, wind, PM, sound pressure level, traffic counter.
 - [ ] testing sensors: particle matter, sound, wind
 - [ ] batteries, solar panels and power regulators

the purpose of this stage is to define a roadmap for a Minimum Viable Product

## Minimum Viable Product

A minimum working configuration 

 - [x] is powered by battery or power supply and optimizes current usage
 - [x] has a simple case (e.g. a junction box) suitable for outdoor usage
 - [x] allows the user to see sensor measures, setup the WiFi connection and global coordinates via a web interface
 - [x] sync its RTC wit NTP servers
 - [x] update the software if available
 - [x] reads sensors data according to the schedule
 - [x] stores data into a queue when network is unreachable 
 - [x] send measurements via ~~existing (sensors.community)~~ and custom APIs or mqtt to a public server
 - [x] receive and display data to a Home Assistant server
 - [ ] basic documentation

# Alpha

 - [ ] project structure pruning and refactoring
 - [ ] software test coverage and debugging
 - [ ] define features and technical details
 - [ ] define metrological details (operating range, uncertainty, redundancy, metrological traceability, calibration) sensors are not black boxes.
 - [ ] design and test of the enclosure, internal layout, bug-proof and water tightness, thermal performance with different climatic conditions and solar exposition
 - [ ] standard visualization via hosted web server
 - [ ] comprehensive documentation and community involvement 
 
# beta
- optional network connection via GSM - LoRa wan.
- test with the help of early users
- collect data
- improved access point interface
- improved visualization server side via Leaflet
