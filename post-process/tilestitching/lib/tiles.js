const R = require("ramda");
const tilebelt = require("@mapbox/tilebelt");

/* images/.../z/x/y.png --> {x, y, z} */
function pathToTile(path) {
  const test = /.*\/([0-9]+)\/([0-9]+)\/([0-9]+)\.png/;
  const match = test.exec(path);
  if (match) {
    return {
      z: parseInt(match[1]),
      x: parseInt(match[2]),
      y: parseInt(match[3])
    };
  } else {
    throw new Error("path not matched");
  }
}

/* [{x, y, z}] => {x0, y0, x1, y1) */
/* Get the min max tile indices */
function getGrid(tiles) {
  const xss = R.map(R.prop("x"), tiles);
  const yss = R.map(R.prop("y"), tiles);
  const x0 = R.reduce(R.min, Infinity, xss);
  const y0 = R.reduce(R.min, Infinity, yss);
  const x1 = R.reduce(R.max, -Infinity, xss);
  const y1 = R.reduce(R.max, -Infinity, yss);

  return { x0, y0, x1, y1 };
}

/* Given tiles at zoom level x, generate a covering of
 * those tiles at zoom level y */
function covering(tiles, zoom) {
  let currZoom = tiles[0].z;
  let currKeys = tiles
    .map(tile => [tile.x, tile.y, tile.z])
    .map(JSON.stringify);
  let cache = new Set(currKeys);

  for (let i = currZoom; i > zoom; i--) {
    let parentTiles = Array.from(cache).map(tileStr => {
      let tile = JSON.parse(tileStr);
      return JSON.stringify(tilebelt.getParent(tile));
    });

    cache = new Set(parentTiles);
  }
  return Array.from(cache).map(JSON.parse).map(tile => {
    return { z: tile[2], y: tile[1], x: tile[0] };
  });
}

/* Given tile at zoom x, get all its children at zoom y */
function getChildren(tile, zoom) {
  if (tile.z === zoom)
    return tile;
  else {
    let children = tilebelt.getChildren([tile.x, tile.y, tile.z]);
    return R.flatten(children.map(tile =>
      getChildren({ x: tile[0], y: tile[1], z: tile[2] }, zoom)));
  }
}

module.exports = {
  pathToTile,
  getGrid,
  covering,
  getChildren
};
