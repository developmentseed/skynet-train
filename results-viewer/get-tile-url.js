const getAccessToken = require('./access-token')

module.exports = function (opts, z, x, y) {
  let url
  if (opts.imagery_source && /^[^\/]+:\/\//.test(opts.imagery_source)) {
    url = opts.imagery_source
  } else {
    url = '//b.tiles.mapbox.com/v4/{mapid}/{z}/{x}/{y}.png?access_token={token}'
      .replace('{mapid}', opts.imagery_source || 'mapbox.satellite')
      .replace('{token}', getAccessToken(opts))
  }

  return url
    .replace('{z}', z)
    .replace('{x}', x)
    .replace('{y}', y)
}
