const fs = require("fs");
const path = require("path");

const listDir = function(dir) {
  const files = fs.readdirSync(dir);
  return files.filter(file => {
    return fs.statSync(path.join(dir, file)).isDirectory();
  });
};

/* Takes a directory and generates a list of tiles*/
module.exports = imagesDir => {
  let paths = [];
  // First level is scenes
  const zooms = fs.readdirSync(imagesDir);
  zooms.forEach(zoom => {
    const xss = listDir(path.join(imagesDir, zoom));
    xss.forEach(x => {
      const yss = fs.readdirSync(path.join(imagesDir, zoom, x));
      yss.forEach(y => {
        if (path.extname(y) === ".png") {
          paths.push(path.join(imagesDir, zoom, x, y));
        }
      });
    });
  });
  return paths;
}
