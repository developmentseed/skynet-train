const cwise = require('cwise');
const ndarray = require('ndarray');

var computeBin = cwise({
  args: ["array", "array", "array", "array"],
  body: function (out, r, g, b) {
    out = (r > 128 || g > 128 || b > 128) ? 255 : 0;
  }
});

/* Image (256, 256, 4) -> ndarray (256, 256)*/
module.exports = function (image) {
  var shape = image.shape.slice(0);
  shape.pop();
  var result = ndarray(new Uint8Array(image.size), shape)
  computeBin(
    result, 
    image.pick(undefined, undefined, 0), 
    image.pick(undefined, undefined, 1), 
    image.pick(undefined, undefined, 2)
  );
  return result;
}
