// utilities
const R = require('ramda');
const getAllPaths = require("./lib/tilepaths");
const { pathToTile, covering, getChildren } = require("./lib/tiles");
const fs = require("fs");

// img
const savePixels = require("save-pixels");
const stitch = require("./lib/img");

// args
const argv = require("minimist")(process.argv.slice(2));

// Paths and tileMap
console.log("Grabbing all paths.");
const allPaths = getAllPaths(argv.dir);
const tiles = allPaths.map(path => {
  const tile = pathToTile(path);
  const hash = `${tile.z}/${tile.x}/${tile.y}`;
  return {tile, hash, path};
});
let tileMap = new Map(R.map(R.props(['hash', 'path']), tiles));

// Compute covering with zoom
const zoom = argv.zoom || 12;
let cover = covering(R.map(R.prop('tile'), tiles), zoom);

// Stitch tiles
cover.forEach(tile => {
stitch(getChildren(tile, 17), tileMap)
  .then(out => {
    // Output
    console.log("Saving output.");
    savePixels(out, "png")
      .pipe(fs.createWriteStream(`out/${tile.z}-${tile.x}-${tile.y}.png`))
      .on("end", function() {
        console.log("Wrapping up.");
      })
      .on("err", err => {
        throw new Error(err);
      });
  })
  .catch(err => {
    console.error("ERROR", err);
  });
});
