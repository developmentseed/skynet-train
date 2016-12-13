#!/usr/bin/env node

var fs = require('fs')
var path = require('path')
var argv = require('minimist')(process.argv.slice(2))
var polyspine = require('polyspine')
var tilebelt = require('tilebelt')
var flatten = require('geojson-flatten')
var normalize = require('geojson-normalize')
var _ = require('lodash')
var distance = require('turf-line-distance')
var simplify = require('turf-simplify')

var input = JSON.parse(fs.readFileSync(path.resolve(__dirname, argv._[0])))
input = normalize(input)
input.features = _.flatten(input.features.map(f => flatten(f)))

// arguments given as filename, then x y z, then distance threshold as ratio of image width
var tile = argv._.slice(1, 4)
var tileBbox = tilebelt.tileToBBOX(tile)

// given image coordinates (0-255), returns geo coordinates
function scale (coords) {
  return [
    coords[0] * (Math.abs(tileBbox[2] - tileBbox[0]) / 255) - tileBbox[0],
    (255 - coords[1]) * (Math.abs(tileBbox[3] - tileBbox[1]) / 255) - tileBbox[1]
  ]
}

var xDistance = distance({
  type: 'LineString',
  coordinates: [
    [tileBbox[0], tileBbox[1]],
    [tileBbox[2], tileBbox[1]]
  ]
})
var thresholdDistance = argv._[4] * xDistance

var scaledInput = {
  type: 'FeatureCollection',
  features: input.features.map(f => {
    return {
      type: f.type,
      properties: f.properties,
      geometry: {
        type: f.geometry.type,
        coordinates: [f.geometry.coordinates[0].map(c => scale(c))]
      }
    }
  })
}

var features = polyspine(scaledInput).map(function (linestring) {
  return {
    type: 'Feature',
    properties: {},
    geometry: {
      type: 'LineString',
      coordinates: linestring
    }
  }
})

var filteredFeatures = features.filter(f => {
  return distance(f) > thresholdDistance && distance(f) < 3 * xDistance
}).map(f => simplify(f, 0.00007))

console.log(filteredFeatures.map(f => JSON.stringify(f)).join('\n'))
