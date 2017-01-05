/* global d3 */

var charts = []

charts.push(createChart(d => +d['#Iters'], d => +d['TrainingLoss']))
charts.push(createChart(d => +d['#Iters'], d => +d['LearningRate']))

function createChart (xvalue, yvalue) {
  // Set the dimensions of the canvas / graph
  var margin = {top: 30, right: 20, bottom: 30, left: 50}
  var width = 600 - margin.left - margin.right
  var height = 270 - margin.top - margin.bottom

  // Set the ranges
  var x = d3.scale.linear().range([0, width])
  var y = d3.scale.linear().range([height, 0])

  // Define the axes
  var xAxis = d3.svg.axis().scale(x)
      .orient('bottom').ticks(5)

  var yAxis = d3.svg.axis().scale(y)
      .orient('left').ticks(5)

  // Define the line
  var valueline = d3.svg.line()
      .x(d => x(xvalue(d)))
      .y(d => y(yvalue(d)))

  // Adds the svg canvas
  var svg = d3.select('body')
      .append('svg')
          .attr('width', width + margin.left + margin.right)
          .attr('height', height + margin.top + margin.bottom)
      .append('g')
          .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')

  // Add the X Axis
  svg.append('g')
     .attr('class', 'x axis')
     .attr('transform', 'translate(0,' + height + ')')
  // Add the Y Axis
  svg.append('g')
     .attr('class', 'y axis')

  getData()
  setInterval(getData, 60000)

  function update (data) {
    svg.selectAll('path').remove()
    svg.append('path')
      .attr('class', 'line')
      .attr('d', valueline(data))
    svg.select('.x.axis').call(xAxis)
    svg.select('.y.axis').call(yAxis)
  }

  return {
    update: function (data) {
      console.log(data.map(d => [xvalue(d), yvalue(d)]))
      // Scale the range of the data
      x.domain(d3.extent(data, xvalue))
      y.domain([0, d3.max(data, yvalue)])
      update(data)
    }
  }
}

function getData () {
  d3.csv('training.csv', function (error, data) {
    if (error) { console.error(error) }
    charts.forEach(chart => chart.update(data))
    const elapsedMin = d3.max(data, d => +d['Seconds']) / 60
    const iterations = d3.max(data, d => +d['#Iters'])
    document.querySelector('#elapsed').innerHTML = Math.round(elapsedMin)
    document.querySelector('#iters_per_min').innerHTML = Math.round(iterations / elapsedMin)
  })
}

