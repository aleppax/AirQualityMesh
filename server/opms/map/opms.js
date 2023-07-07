const api_url = "http://opms.lettori.org/api/api.php";
const map_center = [44.6798, 8.0362];
// data from server is referred to UTC time, 
// the script should display dates with the browser's time offset.
var opmsMap;
var stations = [];
const jca=jscrudapi(api_url,{headers:{'X-API-Key':'RnglFqDTBsVIw6s9-ezOyM685EctG-Qr36dSeJPB96E'}});

function initMap() {
    let mapOptions = {
        preferCanvas: true,
        maxZoom: 16,
        minZoom: 9
    };
    opmsMap = L.map('opmsMap', mapOptions).setView(map_center, 13);
    const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 16,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(opmsMap);
    loadStations();
    opmsMap.on("moveend", loadStations);
    opmsMap.on("click", chartToBackground);
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

async function loadLatestDayRecords(station_id) {
    let station = stations.filter(station => station.id == station_id)[0];
    if (!station.hasOwnProperty('latestDay')) {
        let yesterdayness = new Date(new Date(station.latest.datetime).getTime() - 1000*3600*24).toISOString().split('.')[0] + 'Z'
        let ltst = await jca.list('measurements', {filter:[`station,eq,${station_id}`,`datetime,gt,${yesterdayness}`], order:'datetime,asc'});
        station.latestDay = await ltst.records;
    }
    let label = station.latestDay.map(row => row.datetime);
    let data = [];
    if (station["pm capable ch2"]) {
        data.push({
        label: 'aux PM1.0 ug/m³',
        data: station.latestDay.map(function (row) {if (row["pm1.0_ch2"] != 0) {
                return row["pm1.0_ch2"];
            } else {
                return null;
            }}),
        spanGaps: true,
        borderWidth: 1,
      },{
        label: 'aux PM2.5 ug/m³',
        data: station.latestDay.map(function (row) {if (row["pm2.5_ch2"] != 0) {
                return row["pm2.5_ch2"];
            } else {
                return null;
            }}),
        spanGaps: true,
        borderWidth: 1,
      })
    };
    if (station["pm capable ch1"]) {
        data.push({
        label: 'PM1.0 ug/m³',
        data: station.latestDay.map(row => row["pm1.0"]),
        borderWidth: 1,
        fill: {
            target : 'origin',
        }
      },{
        label: 'PM2.5 ug/m³',
        data: station.latestDay.map(row => row["pm2.5"]),
        borderWidth: 1,
        fill: {
            target : 'origin',
        }
      })
    };
    if (station["temperature capable"]) {
        data.push({
        label: 'temperature '  + station["temperature units"],
        data: station.latestDay.map(row => row["temperature"]),
        borderWidth: 1,
        fill: {
            target : 'origin',
        }
      })
    };
    if (station["humidity capable"]) {
        data.push({
        label: 'humidity '  + station["humidity units"],
        data: station.latestDay.map(row => row["humidity"]),
        borderWidth: 1,
        fill: {
            target : 'origin',
        }
      })
    };
    data.push({
        label: 'vsys voltage V',
        data: station.latestDay.map(row => row["vsys voltage"]),
        borderWidth: 1,
        fill: {
            target : 'origin',
        }
    });
    var oc = Chart.getChart('opmsChart');
    oc.data.labels = label;
    oc.data.datasets = data;
    indexes_of_datasets_to_hide = [];
    oc.data.datasets.forEach(function (val, indx) {
        if (!(["PM2.5 ug/m³","aux PM2.5 ug/m³"].includes(val.label))) {
            indexes_of_datasets_to_hide.push(indx);
            }
        })
    for (const i of indexes_of_datasets_to_hide) {
    oc.getDatasetMeta(i).hidden=true;
    };
    oc.update();
    return;
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
            opmsMap.on("popupopen",function(e) {loadLatestDayRecords(e.popup._contentNode.firstChild.attributes['station'].value);});
            stx.marker = mkx;
            loadLatestRecord(stx).then(colorizeMarker);
            stations.push(stx);
        }
    }
};

function colorizeMarker(statn) {
    //HSL hue from 128(best) to 0(worst), saturation 70, lightness 60
    let htlst = [...statn.marker._icon.firstChild.children];
    //
    let hue = Math.max(0, 128 - (statn.latest["pm2.5"] * 2.56));
    htlst.forEach((item) => {
        if (item.classList.value === "marker1") { 
            item.style.fill = `hsl(${hue}, 70%, 60%)`;
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
