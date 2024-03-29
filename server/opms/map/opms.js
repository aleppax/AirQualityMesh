const api_url = "http://vallecherasca.org/opms/api/api.php";
const map_center = [44.6798, 8.0362];
// data from server is referred to UTC time, 
// the script should display dates with the browser's time offset.
var opmsMap;
var stations = [];
var activeStation = 0
const jca=jscrudapi(api_url,{headers:{'X-API-Key':'RnglFqDTBsVIw6s9-ezOyM685EctG-Qr36dSeJPB96E'}});
let pm25Layer, temperatureLayer, calPm25Layer;


let pm25Gradient = {
    0: "#e5effe",

    2: "#a8cbfe",
    4: "#81b4fe",
    6: "#5a9cfe",
    8: "#3485fd",
    10: "#0d6efd",
    
    12: "#abdee5",
    14: "#86cfda",
    16: "#61c0cf",
    18: "#3cb1c3",
    20: "#17a2b8",

    22: "#b2dfbc",
    24: "#8fd19e",
    26: "#6dc381",
    28: "#4ab563",
    30: "#28a745",

    32: "#fff0a6",
    34: "#ffea7e",
    36: "#ffe356",
    38: "#ffdc2f",
    40: "#ffd607",

    42: "#fed1aa",
    44: "#febc85",
    46: "#fea75f",
    48: "#fd933a",
    50: "#fd7e14",

    52: "#f2b6bc",
    54: "#ed969e",
    56: "#e77681",
    58: "#e25563",
    60: "#dc3546",

    62: "#f0b6e6",
    64: "#ea95dc",
    66: "#e374d1",
    68: "#dd54c6",
    70: "#d633bb",
    
    72: "#cbbbe9",
    74: "#b49ddf",
    76: "#9d7ed5",
    78: "#8660cb",
    80: "#6f42c1",
    
    82: "#6610f2"
};

let mapOptions = {
        preferCanvas: true,
        maxZoom: 19,
        minZoom: 9
    };

let pm25Options = {
        opacity: 0.5,
        maxZoom: mapOptions.maxZoom,
        minZoom: mapOptions.minZoom,
        cellSize: 5,
        exp: 2,
        gradient: pm25Gradient,
        dataType: 2,
        station_range: 10,
        minVal: 0.0,
        maxVal: 150.0
};

//pm25IDWLayer = new L.idwLayer(airboxPoints, pm25IDWOptions);

function initMap() {
    opmsMap = L.map('opmsMap', mapOptions).setView(map_center, 14);
    const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(opmsMap);
    loadStations();
    opmsMap.on("moveend", loadStations);
    opmsMap.on("click", chartToBackground);
    
    pm25Legend = new L.control.opmsLegend(pm25Gradient, {
          position: 'bottomright',
          unit: "μg/m³"
    }).addTo(opmsMap);
};

function averagePM25(chart) {
    var pm25chart = chart.data.datasets.filter(ds => ds.label == "PM2.5 ug/m³");
    if (pm25chart.length === 0) { 
        return 0
    } else {
        pm25data = pm25chart[0].data;
    }
    return pm25data.reduce((a, b) => parseFloat(a) + parseFloat(b), 0) / pm25data.length;
}

const maxpm25 = {
  type: 'line',
  borderColor: 'gray',
  borderDash: [6, 6],
  borderDashOffset: 0,
  borderWidth: 3,
  drawTime: 'beforeDraw',
  label: {
      backgroundColor: 'gray',
      position: 'start',
      content: 'Limite OMS',
      display: true
  },
  scaleID: 'y',
  value: 15
};
const dailyAverage = {
  type: 'line',
  borderColor: (ctx) => {
    if (averagePM25(ctx.chart) < 15) {
        return 'green';
    } else {
        return 'red';
    }
      },
  borderWidth: 3,
  drawTime: 'afterDatasetsDraw',
  label: {
      display: true,
      position: 'start',
      backgroundColor: (ctx) => {
    if (averagePM25(ctx.chart) < 15) {
        return 'green';
    } else {
        return 'red';
    }
      },
      content: (ctx) => {return 'Media giornaliera ' + parseInt(averagePM25(ctx.chart)) + ' ug/m\u{00B3}'},
  },
  scaleID: 'y',
  value: (ctx) => {
      return averagePM25(ctx.chart);
      }
};    
    
function initChart() {
    const data = {};

    const config = {
    type: 'line',
    data: data,
    options: {
        responsive : true,
        maintainAspectRatio: false,
        scales: {
            x: {
                type: 'time',
                adapters: {
                }
            },
            y: {
                beginAtZero: true
        }},
        plugins: {
            legend: {
                onClick: OPMSlegendClickHandler
            },
            annotation: {
                annotations: {
                    maxpm25,dailyAverage
                }
            }
        }
    },
    };
    new Chart(document.getElementById('opmsChart'),
    config
    );
    let oneMoreButton = document.getElementById('oneMoreDay')
    oneMoreButton.addEventListener("click", function() {
        console.log('one more')
        loadMoreDays(activeStation,1)
    });
}

const OPMSlegendClickHandler = function(e, legendItem, legend) {
    const index = legendItem.datasetIndex;
    const ci = legend.chart;
    if (ci.isDatasetVisible(index)) {
        ci.hide(index);
        legendItem.hidden = true;
        if (legendItem.text == "PM2.5 ug/m³") {
            maxpm25.drawTime = null;
            dailyAverage.drawTime = null;
            maxpm25.value = 0;
            dailyAverage.value = 0;
        }
        } else {
        ci.show(index);
        legendItem.hidden = false;
        if (legendItem.text == "PM2.5 ug/m³") {
            maxpm25.drawTime = 'beforeDraw';
            dailyAverage.drawTime = 'afterDatasetsDraw';
            maxpm25.value = 15;
            dailyAverage.value = averagePM25(ci);
        }
    }
    ci.update();
}


async function loadLatestRecord(station) {
    ltst = await jca.list('measurements', {filter:[`station,eq,${station.id}`], order:'id,desc',size:1});
    station.latest = await ltst.records[0];
    return station;
}

function concatDatasets (ds1, ds2) {
  
}

function formatDataset (station) {
    let label = station.latestDay.map(row => row.datetime);
    let dataSets = [];
    if (station["pm capable ch2"]) {
        dataSets.push({
        label: 'aux PM1.0 ug/m³',
        data: station.latestDay.map(function (row) {if (row["pm1.0_ch2"] != 0) {
                return Math.min(Math.max(row["pm1.0_ch2"], 0), 200);
            } else {
                return null;
            }}),
        spanGaps: true,
        borderWidth: 1,
      },{
        label: 'aux PM2.5 ug/m³',
        data: station.latestDay.map(function (row) {if (row["pm2.5_ch2"] != 0) {
                return Math.min(Math.max(row["pm2.5_ch2"], 0), 200);
            } else {
                return null;
            }}),
        spanGaps: true,
        borderWidth: 1,
      })
    };
    if (station["pm capable ch1"]) {
        dataSets.push({
        label: 'PM1.0 ug/m³',
        data: station.latestDay.map(row => Math.min(Math.max(row["pm1.0"], 0), 200)),
        borderWidth: 1,
        fill: {
            target : 'origin',
        }
      },{
        label: 'PM2.5 ug/m³',
        data: station.latestDay.map(row => Math.min(Math.max(row["pm2.5"], 0), 200)),
        borderWidth: 1,
        fill: {
            target : 'origin',
        }
      })
    };
    if (station["temperature capable"]) {
        dataSets.push({
        label: 'temperature '  + station["temperature units"],
        data: station.latestDay.map(row => row["temperature"]),
        borderWidth: 1,
        fill: {
            target : 'origin',
        }
      })
    };
    if (station["humidity capable"]) {
        dataSets.push({
        label: 'humidity '  + station["humidity units"],
        data: station.latestDay.map(row => row["humidity"]),
        borderWidth: 1,
        fill: {
            target : 'origin',
        }
      })
    };
    dataSets.push({
        label: 'vsys voltage V',
        data: station.latestDay.map(row => row["vsys voltage"]),
        borderWidth: 1,
        fill: {
            target : 'origin',
        }
    });
    return [dataSets,label]
}

function hideSomeChartSets (chart) {
    indexes_of_datasets_to_hide = [];
    chart.data.datasets.forEach(function (val, indx) {
        if (!(["PM2.5 ug/m³","aux PM2.5 ug/m³"].includes(val.label))) {
            indexes_of_datasets_to_hide.push(indx);
            }
        })
    for (const i of indexes_of_datasets_to_hide) {
    chart.getDatasetMeta(i).hidden=true;
    };
}

async function downloadRecords (station_id,fromDayAgo,toDayAgo) {
    let station = stations.filter(station => station.id == station_id)[0];
    let todayness = new Date(new Date(station.latest.datetime).getTime() - 1000*3600*24*toDayAgo).toISOString().split('.')[0] + 'Z'
    let fromdayness = new Date(new Date(station.latest.datetime).getTime() - 1000*3600*24*fromDayAgo).toISOString().split('.')[0] + 'Z'
    let ltst = await jca.list('measurements', {filter:[`station,eq,${station_id}`,`datetime,bt,${fromdayness},${todayness}`], order:'datetime,asc'});
    return ltst;
}

function loadMoreDays(station_id,days=1) {
    let station = stations.filter(station => station.id == station_id)[0];
    station.days += days
    downloadRecords(station_id,station.days,station.days-days).then((response) => {
        station.latestDay = response.records.concat(station.latestDay)
        const oc = Chart.getChart('opmsChart')
        let [dataSets,labels] = formatDataset(station)
        oc.data.datasets = dataSets
        oc.data.labels = labels
        hideSomeChartSets(oc)
        oc.update();
    })
}

function loadLatestDayRecords(station_id,days=1) {
    let station = stations.filter(station => station.id == station_id)[0];
    station.days = 1
    downloadRecords(station_id,1,0).then((response) => {
        station.latestDay = response.records
        var oc = Chart.getChart('opmsChart')
        let [dataSets,labels] = formatDataset(station)
        oc.data.datasets = dataSets
        oc.data.labels = labels
        hideSomeChartSets(oc)
        oc.update();
    })
}

function plotStationData(sts) {
    for (let s in sts.records) {
        let stx = sts.records[s];
        // if new
        var exists = stations.filter(obj => {
            return obj.id === stx.id
        });
        if (exists.length === 0) {
            mkx = L.marker(L.latLng(stx.latitude, stx.longitude), {icon:svgIcon}).addTo(opmsMap);
            let mkx_content = `<div class="leaflet-control-layers-base" station="${stx.id}"> <table> <tr> <td>station ID: </td><td>${stx.id}</td></tr><tr> <td>Name: </td><td>${stx.name}</td></tr><tr> <td>purpose: </td><td>${stx['station purpose']}</td></tr><tr> <td>Location: </td><td>Lat. ${stx.latitude} - Lon. ${stx.longitude}</td></tr><tr> <td>altitude msl: </td><td>${stx['altitude msl']}</td></tr><tr> <td>Height above ground: </td><td>${stx['height above ground']}cm</td></tr><tr> <td><input type="checkbox" name="PM channel 1" onclick="return false;" ${(stx['pm capable ch1']==1) ? 'checked' : ''}/> PM channel 1</td><td><input type="checkbox" name="PM channel 2" onclick="return false;" ${(stx['pm capable ch2']==1) ? 'checked' : ''}/> PM channel 2</td></tr><tr> <td><input type="checkbox" name="sound pressure" onclick="return false;" ${(stx['sound pressure capable']==1) ? 'checked' : ''}/> sound pressure</td><td><input type="checkbox" name="barometric pressure" onclick="return false;" ${(stx['barometric pressure capable']==1) ? 'checked' : ''}/> barometric pressure</td></tr><tr> <td><input type="checkbox" name="temperature" onclick="return false;" ${(stx['temperature capable']==1) ? 'checked' : ''}/> temperature</td><td><input type="checkbox" name="wind direction" onclick="return false;" ${(stx['wind direction capable']==1) ? 'checked' : ''}/> wind direction</td></tr><tr> <td><input type="checkbox" name="wind speed" onclick="return false;" ${(stx['wind speed capable']==1) ? 'checked' : ''}/> wind speed</td><td><input type="checkbox" name="humidity" onclick="return false;" ${(stx['humidity capable']==1) ? 'checked' : ''}/> humidity</td></tr><tr> <td><input type="checkbox" name="vehicle count" onclick="return false;" ${(stx['vehicle count capable']==1) ? 'checked' : ''}/> vehicle count</td><td><img class="chartIcon" src="chartIcon.jpg" alt="last day chart" onclick="chartToForeground()"/></td></tr></table> </div><div> <a id="idw-display-close-button" class="leaflet-popup-close-button" href="#close">×</a> </div>`;
            mkx.bindPopup(mkx_content,{offset : L.point(3, -32)});
            opmsMap.on("popupopen",function(e) {
              activeStation = e.popup._contentNode.firstChild.attributes['station'].value
              loadLatestDayRecords(activeStation);});
            stx.marker = mkx;
            loadLatestRecord(stx).then(colorizeMarker);
            stations.push(stx);
        }
    }
};

function colorizeMarker(statn) {
    let htlst = [...statn.marker._icon.firstChild.children];
    let colorIndex = 2 * Math.round(statn.latest["pm2.5"] / 2);
    colorIndex = Math.min(Math.max(colorIndex, 0), 82);
    let color = pm25Gradient[colorIndex]; 
    htlst.forEach((item) => {
        if (item.classList.value === "marker1") { 
            item.style.fill = color;
    }});
};

function chartToForeground() {
    document.getElementById("cnvBox").style.zIndex = "15";
}

function chartToBackground() {
    document.getElementById("cnvBox").style.zIndex = "5";
}

async function loadStations() {
    let nesw = opmsMap.getBounds()
    if (nesw['_northEast'].lng > nesw['_southWest'].lng) {
        var stl = jca.list('stations',{filter:[`latitude,bt,${nesw['_southWest'].lat},${nesw['_northEast'].lat}`,`longitude,bt,${nesw['_southWest'].lng},${nesw['_northEast'].lng}`]});
    } else {
        var stl = jca.list('stations',{filter:[`latitude,bt,${nesw['_southWest'].lat},${nesw['_northEast'].lat}`,`longitude,lt,${nesw['_northEast'].lng}`],
                                            filter1:[`latitude,bt,${nesw['_southWest'].lat},${nesw['_northEast'].lat}`,`longitude,gt,${nesw['_southWest'].lng}`]});
    }
    stl.then((st) => plotStationData(st));
};

const svgIcon = L.divIcon({
  html: `<svg version="1.1" viewBox="0 0 24 40" xmlns="http://www.w3.org/2000/svg"><path d="m7.9033 28.05c1.7991 3.3632 3.2845 6.992 4.1269 11.353 1.2188-6.6157 4.0018-11.444 6.9668-16.178 0.99544-1.5894 1.9874-3.1779 2.7785-4.9115 0.4053-0.88813 0.86085-1.7196 1.1441-2.7143 0.27988-0.98269 0.47855-2.1674 0.44949-3.4467-0.056764-2.497-0.73346-4.4113-1.7162-6.0317-21.658 2.3052-21.208 8.1045-13.75 21.93z" class="marker1"/><ellipse id="point" class="marker1" cx="12" cy="6" rx="5" ry="5" clip-rule="evenodd" fill-rule="evenodd" style="stroke-width:1.2;stroke: #555;fill-opacity: 1.0;opacity:1;"/><path d="m16.106 28.05c-1.7991 3.3632-3.2845 6.992-4.1269 11.353-1.2188-6.6157-4.0018-11.444-6.9668-16.178-0.99545-1.5894-1.9874-3.1779-2.7785-4.9115-0.4053-0.88813-0.86085-1.7196-1.1441-2.7143-0.27988-0.98269-0.47855-2.1674-0.44949-3.4467 0.056763-2.497 0.73346-4.4113 1.7162-6.0317 21.658 2.3052 21.208 8.1045 13.75 21.93z" class="marker1"/><path id="mark" d="m12.03 39.402c-0.84245-4.3606-2.3278-7.9894-4.1269-11.353-1.3345-2.4947-2.8804-4.7974-4.3108-7.2165-0.47749-0.80759-0.88957-1.6608-1.3484-2.4989-0.91743-1.6759-1.6613-3.6189-1.614-6.1394 0.04618-2.4626 0.72167-4.4381 1.6957-6.0533 1.602-2.6565 4.2855-4.8346 7.8861-5.407 2.9439-0.468 5.704 0.32268 7.6614 1.5295 1.5995 0.98618 2.8381 2.3035 3.7796 3.856 0.98271 1.6204 1.6594 3.5347 1.7162 6.0317 0.02905 1.2793-0.16962 2.464-0.4495 3.4467-0.28325 0.99468-0.73879 1.8261-1.1441 2.7143-0.79117 1.7337-1.7831 3.3221-2.7785 4.9116-2.965 4.7342-5.748 9.5623-6.9668 16.178z" clip-rule="evenodd" fill="#fff" fill-rule="evenodd" stroke="#555" stroke-miterlimit="10" stroke-width=".82566" style="fill:none;stroke-linejoin:round;stroke-width:1.2;stroke:#333"/></svg>`,
  className: "",
  iconSize: [30, 50],
  iconAnchor: [12, 40],
});

initMap();
initChart();
