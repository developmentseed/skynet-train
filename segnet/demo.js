const qs = require('querystring')
const http = require('choo/http')
const tilebelt = require('tilebelt')
const createMap = require('../results-viewer/map')
const getSatelliteTileURL = require('../results-viewer/get-tile-url')

const query = qs.parse(window.location.search.substring(1))

let map = createMap(query).on('load', function () {
  map.addSource('tile', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
  map.addLayer({
    'id': 'tile',
    'source': 'tile',
    'type': 'line',
    'paint': {
      'line-color': 'red',
      'line-width': 4
    }
  })
})
.on('click', onClick)

function onClick (event) {
  var loc = event.lngLat
  var tile = tilebelt.pointToTile(loc.lng, loc.lat, 17)
  var [w, s, e, n] = tilebelt.tileToBBOX(tile)
  var z = +tile[2]

  var coordinates = [
    [w, n],
    [e, n],
    [e, s],
    [w, s]
  ]

  map.getSource('tile').setData({
    type: 'Feature',
    properties: {},
    geometry: {
      type: 'Polygon',
      coordinates: [ coordinates.concat([[w, n]]) ]
    }
  })

  var inputImageURL = getSatelliteTileURL(query, tile[2], tile[0], tile[1])
  http.get({ url: inputImageURL, responseType: 'arraybuffer' }, function (err, response, body) {
    if (err) { console.error(err); return }
    var blob = new Blob([body], {type: 'image/png'})
    var fd = new window.FormData()
    fd.append('image', blob)
    http.post({
      url: '/predict',
      body: fd,
      responseType: 'arraybuffer'
    }, function (err, response, body) {
      if (err) { console.error(err); return }
      var blob = new Blob([body], {type: 'image/png'})
      var outputUrl = URL.createObjectURL(blob)
      map.jumpTo({center: [ (w + e) / 2, (s + n) / 2 ], zoom: z - 1, speed: 2})
      showOverlay(outputUrl, coordinates)
    })
  })
}

function showOverlay (url, coords) {
  if (map.getLayer('class-overlay')) {
    map.removeLayer('class-overlay')
  }
  if (map.getSource('class-overlay')) {
    map.removeSource('class-overlay')
  }

  map.addSource('class-overlay', {
    type: 'image',
    url: url,
    coordinates: coords
  })

  map.on('render', addImageLayer)
  function addImageLayer () {
    if (map.getSource('class-overlay').loaded()) {
      map.off('render', addImageLayer)
      map.addLayer({
        'id': 'class-overlay',
        'source': 'class-overlay',
        'type': 'raster',
        'paint': { 'raster-opacity': 0.5 }
      })
    }
  }
}

