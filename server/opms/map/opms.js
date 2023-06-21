const api_url = "http://opms.local/api/api.php";
map_center = [44.6798, 8.0362]
var map, data;
const jca=jscrudapi(api_url);
jca.list('stations');

function initMap() {
    map = L.map('opms').setView(map_center, 13);
    const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
}

initMap();
