
   // create a Leaflet map
   var map = L.map('map').setView([51.505, -0.09], 13);

   // create a popup and add it to a marker on the map
   var popup = L.popup()
       .setLatLng([51.5, -0.09])
       .setContent('<canvas id="chart"></canvas>')
       .openOn(map);
   
   // create a new Chart.js chart inside the popup
   var chartCanvas = document.getElementById('chart');
   var chart = new Chart(chartCanvas, {
       type: 'bar',
       data: {
           labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
           datasets: [{
               label: 'My Dataset',
               data: [12, 19, 3, 5, 2, 3, 7],
               backgroundColor: 'rgba(255, 99, 132, 0.2)',
               borderColor: 'rgba(255, 99, 132, 1)',
               borderWidth: 1
           }]
       },
       options: {
           scales: {
               yAxes: [{
                   ticks: {
                       beginAtZero: true
                   }
               }]
           }
       }
   });

   const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);