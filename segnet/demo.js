const qs = require('querystring')
const http = require('choo/http')
const mapboxgl = require('mapbox-gl')
const tilebelt = require('tilebelt')

const query = qs.parse(window.location.search.substring(1))
const baseurl = query.baseurl || ''

mapboxgl.accessToken = query.access_token
const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/satellite-v8',
  center: [-122.4, 47.6],
  zoom: 11,
  hash: true
})
.on('load', function () {
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


function getSatelliteTileURL(tile) {
  return 'http://b.tiles.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png'
    .replace('{z}', tile[2])
    .replace('{x}', tile[0])
    .replace('{y}', tile[1]) +
    '?access_token=' + query.access_token
}

function onClick (event) {
  var loc = event.lngLat
  var tile = tilebelt.pointToTile(loc.lng, loc.lat, 17)
  var bbox = tilebelt.tileToBBOX(tile)
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
      coordinates: [ coordinates.concat([[w,n]]) ]
    }
  })



  var inputImageURL = getSatelliteTileURL(tile)
  http.get({ url: inputImageURL, responseType: 'arraybuffer' }, function (err, response, body) {
    var blob = new Blob([body], {type: 'image/png'})
    var fd = new window.FormData()
    fd.append('image', blob)
    http.post({
      url: '/predict',
      body: fd,
      responseType: 'arraybuffer'
    }, function (err, response, body) {
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

