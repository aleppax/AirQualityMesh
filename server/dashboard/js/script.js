var ctx = document.getElementById('myChart');

var stars = [135850, 52122, 148825, 16939, 9763];
var frameworks = ['React', 'Angular', 'Vue', 'Hyperapp', 'Omi'];


var dataset_pie= [{
    label: 'Github Stars',
    data: stars,
    backgroundColor: [
        "rgba(255, 99, 132, 0.2)",
        "rgba(54, 162, 235, 0.2)",
        "rgba(255, 206, 86, 0.2)",
        "rgba(75, 192, 192, 0.2)",
        "rgba(153, 102, 255, 0.2)"
        ],
    borderColor: [
        "rgba(255, 99, 132, 1)",
        "rgba(54, 162, 235, 1)",
        "rgba(255, 206, 86, 1)",
        "rgba(75, 192, 192, 1)",
        "rgba(153, 102, 255, 1)",
        ],
    borderWidth: 1
}]

var dataset_line= [{
    label: 'Github Stars LINE',
    data: stars,
    backgroundColor: "rgba(255, 99, 132, 0.2)",
    borderColor: "rgba(255, 99, 132, 1)",
    borderWidth: 1,
    fill: false,
    lineTension: 0
}]

var myChart = new Chart(ctx, {
    type: 'line',    //'bar' or  'pie'
    data: {
       labels: frameworks,
       datasets: dataset_line  //'bar'
    }
   })
   