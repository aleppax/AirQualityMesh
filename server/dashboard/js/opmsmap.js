//opmsmap.js
const api_stations_url = "https://lettori.org/opms/api.php/records/stations";
const intervalMlS = 24 * 60 * 60 * 1000; // 24h of data logs
const validityMeasureS = 60 * 60 * 1000; // if more than xxx old, measure is not used for display
const nowness = new Date();

api_data_url = 'https://lettori.org/opms/api.php/records/measurements?filter=datetime,gt,';
const map_center = [44.6798, 8.0362]
var map, data;
var stations = [];

//Marker Letter
var myIconA= L.icon({
    iconUrl: 'img/Iconarchive-Red-Orb-Alphabet-Letter-A.64.png',
    iconsize:[64,64]
    })
var myIconR= L.icon({
    iconUrl: 'img/Iconarchive-Red-Orb-Alphabet-Letter-R.64.png',
    iconsize:[64,64]
    })
/* var googlesat= L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{
    maxZoom: 20,
    subdomains:['mt0','mt1','mt2','mt3']
    }); */
/* var osm= L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }) */


function initMap() {
    map = L.map('map').setView(map_center, 15);
    const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

} 

function initControls() {
    // timeline slider
    // Leaflet overlay
    var singleMarker = L.marker([44.691542, 8.025636], { icon: myIconA, draggable: true });
    var popup = singleMarker
        .bindPopup('This is the Alba. ' + singleMarker.getLatLng())
        .openPopup()
    popup.addTo(map); 

    var secondMarker = L.marker([44.687, 8.04], { icon: myIconR, draggable: true });
    var popupchart = secondMarker
        .bindPopup('test')
        .openPopup()
    
    L.geoJSON(features)
        .addTo(map)
        .bindPopup(chart);

        // per prendere lat e lon di un punto sulla mappa 
   /*  map.on('click', function(e) {
            alert("Lat, Lon : " + e.latlng.lat + ", " + e.latlng.lng)
        });    */ 

    
    var overlayMaps = {
        "First Marker": singleMarker,
        'Second Marker': secondMarker
    }; 
        
    L.control.layers(overlayMaps).addTo(map);


    //chart example

    // measurand selector or none
    
    // 
}

// fetch stations
async function fetchStations() {
    const response = await fetch(api_stations_url);
    const stations_json = await response.json();
    return stations_json;
}

async function loadStations(sts) {
    for (let st in sts) {
        let station = sts[st];
        station.marker = L.marker([station.latitude, station.longitude]).bindPopup(station.name).addTo(map);
        if (station.name == "prototipo 1") {posA=L.marker([station.latitude, station.longitude], {icon : myIconA}).bindPopup(station.name).addTo(map);}
        if (station.name == "prototipo 2") {posR=L.marker([station.latitude, station.longitude], {icon : myIconR}).bindPopup(station.name).addTo(map);}
        stations.push(station)
    }
    
    return stations
}

// fetch current data measured by stations
async function fetchData(date) {
    const response = await fetch(api_data_url + date);
    const data_json = await response.json();
    return data_json;
}

async function initData() {
    let numberOfMlSeconds = nowness.getTime();
    let modDateObj = new Date(numberOfMlSeconds - intervalMlS);
    fromISOdate = modDateObj.toISOString();
    data = await fetchData(fromISOdate);
    data = data.records;
    data.rbys = {};
}

function initHeatMap(sts) {
    const st_for_map = sts.map((
    { id, latitude, longitude }) => ({ id, latitude, longitude}));
    for (st in stations) {
        st_for_map[st].value = 45;
    }  
    let testData = {
        max: 50,
        min: 0,
        data: st_for_map
    };

    var cfg = {
      // radius should be small ONLY if scaleRadius is true (or small radius is intended)
      "radius": 0.002,
      "maxOpacity": .6, 
      // scales the radius based on map zoom
      "scaleRadius": true, 
      // if set to false the heatmap uses the global maximum for colorization
      // if activated: uses the data maximum within the current map boundaries 
      //   (there will always be a red spot with useLocalExtremas true)
      "useLocalExtrema": false,
      // which field name in your data represents the latitude - default "lat"
      latField: 'latitude',
      // which field name in your data represents the longitude - default "lng"
      lngField: 'longitude',
      // which field name in your data represents the data value - default "value"
      valueField: 'value'
    };
    
    var heatmapLayer = new HeatmapOverlay(cfg);
    map.addLayer(heatmapLayer)
    heatmapLayer.setData(testData);
}

var features = { "type":"featureCollection", features: [
    {
      "type":"Feature",
      "properties":{data:[10,12,16,20,25,30,30,29,13,10,7,6],title:"some funny data"},
      "geometry":{
        "type":"Polygon",   // si usa longitudine e latitudine
        //"coordinates":[[[17.385044, 78.486671],        [16.506174, 80.648015],         [17.686816, 83.218482]]]
        "coordinates":[[[ 8.037009817420332,44.69056260302635],[ 8.045589725887831,44.68964732052009],[ 8.044431438244711,44.6841320649042,],[ 8.03533673526919,44.68623013803223]]]
        //"coordinates":[[[-0.1398611068725586,51.50203767899114],[-0.13994693756103516,51.50142324743368],[-0.13887405395507812,51.50051494213073],[-0.13063430786132812,51.501369818211096],[-0.1299905776977539,51.50144996202149],[-0.12973308563232422,51.50281238523426],[-0.12921810150146484,51.503400084633526],[-0.12926101684570312,51.504014489537944],[-0.12943267822265625,51.504575460694184],[-0.1295614242553711,51.50502957514356],[-0.13084888458251953,51.505724094371274],[-0.1398611068725586,51.50203767899114]]]
      }
    },
    {
      "type": "Feature",
      "properties": {data:[100,112,130,200,210,190,170,160,150,140,110,100],title:"Some Statistic"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-0.14938831329345703,51.503132949482534],[-0.1494741439819336,51.502625388381375],[-0.14200687408447266,51.502358248689035],[-0.14127731323242188,51.502732243819835],[-0.1403331756591797,51.50281238523426],[-0.13956069946289062,51.50251853269236],[-0.13441085815429688,51.504869299972306],[-0.1347970962524414,51.50510971251776],[-0.13956069946289062,51.50329323076107],[-0.14265060424804688,51.506739141893],[-0.14664173126220703,51.50468231156],[-0.14732837677001953,51.504148054725356],[-0.14938831329345703,51.503132949482534]]]
     }
    }
  ]};

  
function chart(d) {
    var feature = d.feature;
    var data = feature.properties.data;
    
    var width = 300;
    var height = 80;
    var margin = {left:20,right:15,top:40,bottom:40};
    var parse = d3.timeParse("%m");
    var format = d3.timeFormat("%b");
     
    var div = d3.create("div")
    var svg = div.append("svg")
      .attr("width", width+margin.left+margin.right)
      .attr("height", height+margin.top+margin.bottom);
    var g = svg.append("g")
      .attr("transform","translate("+[margin.left,margin.top]+")");
      
    var y = d3.scaleLinear()
      .domain([0, d3.max(data, function(d) { return d; }) ])
      .range([height,0]);
      
    var yAxis = d3.axisLeft()
      .ticks(4)
      .scale(y);
    g.append("g").call(yAxis);
      
    var x = d3.scaleBand()
      .domain(d3.range(12))
      .range([0,width]);
      
    var xAxis = d3.axisBottom()
      .scale(x)
      .tickFormat(function(d) { return format(parse(d+1)); });
      
    g.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .selectAll("text")
        .attr("text-anchor","end")
        .attr("transform","rotate(-90)translate(-12,-15)")
      
    var rects = g.selectAll("rect")
      .data(data)
      .enter()
      .append("rect")
      .attr("y",height)
      .attr("height",0)
      .attr("width", x.bandwidth()-2 )
      .attr("x", function(d,i) { return x(i); })
      .attr("fill","steelblue")
      .transition()
      .attr("height", function(d) { return height-y(d); })
      .attr("y", function(d) { return y(d); })
      .duration(1000);
      
    var title = svg.append("text")
      .style("font-size", "20px")
      .text(feature.properties.title)
      .attr("x", width/2 + margin.left)
      .attr("y", 30)
      .attr("text-anchor","middle");
      
    return div.node();
      
  }   
// use a canvas for overlay display of sensor chart

initMap()
initData();
fetchStations().then(st => loadStations(st.records)).then(st => initHeatMap(st));
initControls();
