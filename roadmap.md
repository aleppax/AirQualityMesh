# Roadmap

## Early Proof of Concept

we are investigating many possibilities and the purpose of this stage is to define a roadmap for the Proof of Concept

## Proof of Concept -CURRENT-

At this stage the project is emerging from a glowing cauldron, nothing is permanent and the overall structure of the system is in progress.
We are currently evaluating:

- WiFi network, data queue, main routine
- acting as an Access Point and web server to retrieve the SSID and password from the user (unsecured)
- MQTT connection,REST API
- selection of parameters: humidity, temperature, particle matters, sound pressure level
- testing sensors: particle matter, sound, wind
- batteries, solar panels and power regulators

the purpose of this stage is to define a roadmap for a Minimum Viable Product

## Minimum Viable Product

A minimum working configuration 

- is powered by battery or power supply and optimizes current usage
- has a simple case (e.g. a junction box) suitable for outdoor usage
- allows the user to see sensor measures, setup the WiFi connection and the GPS data via web interface
- sync its RTC wit NTP servers
- update the software if available
- reads sensors data according to the schedule
- stores data into a queue when network is unreachable 
- send measurements via existing (sensors.community) and custom APIs or mqtt to a public server
- receive and display data to a Home Assistant server
- basic documentation

# Alpha

- project structure pruning and refactoring
- software test coverage and debugging
- define features and technical details
- define metrological details (operating range, uncertainty, redundancy, metrological traceability, calibration) sensors are not black boxes.
- design and test of the enclosure, internal layout, bug-proof and water tightness, thermal performance with different climatic conditions and solar exposition
- standard visualization via hosted web server
- comprehensive documentation and community involvement 
 
# beta
- optional network connection via GSM - LoRa wan.
- test with the help of early users
- collect data
- improved access point interface
- improved visualization server side via Leaflet
