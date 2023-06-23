const api_url = "http://opms.local/api/api.php";
const map_center = [44.6798, 8.0362];
const clampPM = 50; // ppm max to scale the color map
var map;
var stations = [];
const jca=jscrudapi(api_url);

function initMap() {
    map = L.map('opms').setView(map_center, 13);
    const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    loadStations();
    map.on("moveend", loadStations());
};

async function loadLatestRecord(station) {
    ltst = await jca.list('measurements', {filter:[`station,eq,${station.id}`], order:'id,desc',size:1});
    station.latest = await ltst.records[0];
    return station;
}

function plotStationData(sts) {
    for (let s in sts.records) {
        let stx = sts.records[s];
        // if new
        var exists = stations.filter(obj => {
            return obj.id === stx.id
        });
        if (exists.length === 0) {
            mkx = L.marker(L.latLng(stx.latitude, stx.longitude), {icon:svgIcon}).addTo(map);
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

async function loadStations() {
    let nesw = map.getBounds()
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
  iconSize: [36, 60],
  iconAnchor: [12, 40],
});

initMap();
