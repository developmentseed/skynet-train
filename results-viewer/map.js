const mapboxgl = require('mapbox-gl')
const labelLayers = require('mapbox-gl-styles/styles/basic-v9.json').layers
    .filter((l) => /poi|place|country/.test(l.id))
const getAccessToken = require('./access-token')

module.exports = function (opts) {
  let style
  if (opts.imagery_source) {
    let source
    if (!/^[^\/]+:\/\//.test(opts.imagery_source)) {
      source = { url: 'mapbox://' + opts.imagery_source }
    } else {
      source = { tiles: [ opts.imagery_source ] }
    }
    Object.assign(source, { type: 'raster', tileSize: 256 })
    style = {
      version: 8,
      sources: {
        mapbox: { url: 'mapbox://mapbox.mapbox-streets-v7', type: 'vector' },
        imagery: source
      },
      sprite: 'mapbox://sprites/mapbox/basic-v9',
      glyphs: 'mapbox://fonts/mapbox/{fontstack}/{range}.pbf',
      layers: [
        {id: 'background', type: 'background', paint: { 'background-color': '#121212' }},
        {id: 'imagery', type: 'raster', source: 'imagery'}
      ].concat(labelLayers)
    }
  } else {
    style = 'mapbox://styles/mapbox/satellite-streets-v9'
  }

  mapboxgl.accessToken = getAccessToken(opts)
  const map = new mapboxgl.Map({
    container: opts.container || 'map',
    style: style,
    center: [0, 0],
    zoom: 1,
    hash: true
  })

  if (opts.showTileBoundaries) {
    map.showTileBoundaries = true
  }

  return map
}

