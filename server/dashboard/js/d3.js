var features = { "type":"featureCollection", features: [
    {
      "type":"Feature",
      "properties":{data:[10,12,16,20,25,30,30,29,13,10,7,6],title:"Injuries Due to Swan Bite by Month"},
      "geometry":{
        "type":"Polygon",
          "coordinates":[[[-0.1398611068725586,51.50203767899114],[-0.13994693756103516,51.50142324743368],[-0.13887405395507812,51.50051494213073],[-0.13063430786132812,51.501369818211096],[-0.1299905776977539,51.50144996202149],[-0.12973308563232422,51.50281238523426],[-0.12921810150146484,51.503400084633526],[-0.12926101684570312,51.504014489537944],[-0.12943267822265625,51.504575460694184],[-0.1295614242553711,51.50502957514356],[-0.13084888458251953,51.505724094371274],[-0.1398611068725586,51.50203767899114]]]
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
  
  var mymap = L.map('mapid').setView([51.5, -0.14], 14);
  
/*  L.tileLayer('http://{s}.tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(mymap); */
   L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(mymap); 
  
  L.geoJSON(features)
    .addTo(mymap)
    .bindPopup(chart);
      
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
  