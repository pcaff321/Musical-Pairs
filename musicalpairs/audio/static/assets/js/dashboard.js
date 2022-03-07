/* globals Chart:false, feather:false */

(function () {
    'use strict'
  
    feather.replace({ 'aria-hidden': 'true' })
  
    // Graphs
    var ctx = document.getElementById('myChart')
    const d = new Date();
    var d1 = new Date(new Date().setDate(new Date().getDate() - 1));
    var d2 = new Date(new Date().setDate(new Date().getDate() - 2));
    var d3 = new Date(new Date().setDate(new Date().getDate() - 3));
    var d4 = new Date(new Date().setDate(new Date().getDate() - 4));
    var d5 = new Date(new Date().setDate(new Date().getDate() - 5));
    var d6 = new Date(new Date().setDate(new Date().getDate() - 6));
    // eslint-disable-next-line no-unused-vars
    var myChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [
         d6.toLocaleDateString("en-GB"),
         d5.toLocaleDateString("en-GB"),
         d4.toLocaleDateString("en-GB"),
         d3.toLocaleDateString("en-GB"),
         d2.toLocaleDateString("en-GB"),
         d1.toLocaleDateString("en-GB"),
          d.toLocaleDateString("en-GB")
        ],
        datasets: [{
          data: [
            mylist[6],
            mylist[5],
            mylist[4],
            mylist[3],
            mylist[2],
            mylist[1],
            mylist[0]
          ],
          lineTension: 0,
          backgroundColor: 'transparent',
          borderColor: '#007bff',
          borderWidth: 4,
          pointBackgroundColor: '#007bff'
        }]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: false
            }
          }]
        },
        legend: {
          display: false
        }
      }
    })
  })()
  