const qs = require('querystring')
const http = require('choo/http')
const tilebelt = require('tilebelt')
const createMap = require('../results-viewer/map')
const getSatelliteTileURL = require('../results-viewer/get-tile-url')

const query = qs.parse(window.location.search.substring(1))

const predictions = window.location.href.replace(/static.*$/, 'index.json')

let map = createMap(query).on('load', function () {
  map.addSource('prediction', {
    type: 'raster',
    tileSize: 256,
    url: predictions
  })
  map.addLayer({
    id: 'prediction',
    type: 'raster',
    source: 'prediction',
    paint: {
      'raster-opacity': 0.5
    }
  })
})

