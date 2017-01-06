/* global d3 */

var charts = []

charts.push(createChart(d => +d['#Iters'], d => +d['TrainingLoss'], d => +d['SmoothedLoss']))
charts.push(createChart(d => +d['#Iters'], d => +d['LearningRate']))

function createChart (xvalue, yvalue, linevalue) {
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
      .interpolate('basis')
      .x(d => x(xvalue(d)))
      .y(d => y(linevalue(d)))

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
    const circle = svg.selectAll('circle')
      .data(data)

    circle.enter().append('circle').attr('class', 'point')
    circle
      .attr('cx', d => x(xvalue(d)))
      .attr('cy', d => y(yvalue(d)))
      .attr('r', 1)

    if (linevalue) {
      svg.append('path')
        .attr('class', 'line')
        .attr('d', valueline(data))
    }

    svg.select('.x.axis').call(xAxis)
    svg.select('.y.axis').call(yAxis)
  }

  return {
    update: function (data) {
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

    data.sort((da, db) => da['#Iters'] - db['#Iters'])
    data.forEach((d, i) => {
      let delta = i ? d['Seconds'] - data[i - 1]['Seconds'] : 0
      if (delta < 0) {
        // this happens at the boundary between log files (every 10000 iterations)
        delta = 0
      }
      d['DeltaSeconds'] = delta
    })

    console.log(data)

    const kernel = normaliseKernel([0.1, 0.2, 0.3, 0.2, 0.1]) // gaussian smoothing
    convolute(data, kernel, d => +d['TrainingLoss'], 'SmoothedLoss')

    charts.forEach(chart => chart.update(data))
    const elapsedMin = d3.sum(data, d => +d['DeltaSeconds']) / 60
    const iterations = d3.max(data, d => +d['#Iters'])
    document.querySelector('#iters').innerHTML = Math.round(iterations)
    document.querySelector('#elapsed').innerHTML = Math.round(elapsedMin)
    document.querySelector('#iters_per_min').innerHTML = Math.round(iterations / elapsedMin)
  })
}

// from http://bl.ocks.org/tomgp/6770520
function convolute (data, kernel, accessor, target) {
  var kernelCenter = Math.floor(kernel.length / 2)
  // var leftSize = kernelCenter
  // var rightSize = kernel.length - (kernelCenter - 1)
  if (accessor === undefined) {
    accessor = function (datum) {
      return datum
    }
  }

  function constrain (i, range) {
    if (i < range[0]) {
      i = 0
    }
    if (i > range[1]) {
      i = range[1]
    }
    return i
  }

  data.forEach(function (d, i) {
    var s = 0
    for (var k = 0; k < kernel.length; k++) {
      var index = constrain((i + (k - kernelCenter)), [0, data.length - 1])
      s += kernel[k] * accessor(data[index])
    }
    data[i][target] = s
  })
}

function normaliseKernel (a) {
  function arraySum (a) {
    var s = 0
    for (var i = 0; i < a.length; i++) {
      s += a[i]
    }
    return s
  }
  var sumA = arraySum(a)
  var scaleFactor = sumA / 1
  a = a.map(function (d) {
    return d / scaleFactor
  })
  return a
}
