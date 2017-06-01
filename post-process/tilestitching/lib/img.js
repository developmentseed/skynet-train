const zeros = require("zeros");
const Promise = require("bluebird");
const getPixels = Promise.promisify(require("get-pixels"));

const binary = require("./binary");
const { getGrid } = require("./tiles");

/* Fills an image with a subimage*/
function fill(out, pixels, xoffset, yoffset) {
  for (let i = 0; i < 256; i++) {
    for (let j = 0; j < 256; j++) {
      if (pixels) {
        out.set(xoffset + i, yoffset + j, pixels.get(i, j));
      } else {
        out.set(xoffset + i, yoffset + j, 0);
      }
    }
  }
  return out;
}

/* Takes tiles and a tileMap from tile to image
  * and forms a stitched tile */
async function stitch(tiles, tileMap) {
  console.log(tiles);
  let length = tiles.length;
  const grid = getGrid(tiles);

  const width = (grid.x1 + 1 - grid.x0) * 256;
  const height = (grid.y1 + 1 - grid.y0) * 256;

  console.log("Zeroing out matrix.");
  let out = zeros([width, height], "uint8");

  return Promise.mapSeries(tiles, async (tile, idx) => {
    console.log(`${idx}/${length}:`, tile);
    const path = tileMap.get(`${tile.z}/${tile.x}/${tile.y}`);
    const xoffset = (tile.x - grid.x0) * 256;
    const yoffset = (tile.y - grid.y0) * 256;

    let pixels = null;
    if (path) {
      const image = await getPixels(path);
      pixels = binary(image);
    }

    // If pixels is null, it will fill with black
    return fill(out, pixels, xoffset, yoffset);
  }).then(() => out);
}

module.exports = stitch;
