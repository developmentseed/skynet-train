#!/usr/bin/env node

const fs = require('fs')
const cover = require('tile-cover')

const data = JSON.parse(fs.readFileSync(process.argv[2]))
const minZoom = process.argv[3]
const maxZoom = process.argv[4] || minZoom
go(data)

function go (g) {
  if (Array.isArray(g)) {
    return g.forEach(go)
  } else if (g.type === 'FeatureCollection') {
    return g.features.forEach(go)
  } else if (g.type === 'Feature') {
    return go(g.geometry)
  }
  // else if (g.type === 'MultiPolygon') {
  //   return g.coordinates.forEach(polygonCoords => {
  //     const geom = {
  //       type: 'Polygon',
  //       coordinates: polygonCoords
  //     }
  //     go(geom)
  //   })
  // }

  const tiles = cover.tiles(g, {
    min_zoom: parseInt(minZoom, 10),
    max_zoom: parseInt(maxZoom, 10)
  })
  tiles.forEach(tile => console.log(JSON.stringify(tile)))
}

