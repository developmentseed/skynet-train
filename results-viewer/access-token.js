module.exports = function getAccessToken (opts) {
  var accessToken =
      opts.access_token ||
      localStorage.getItem('accessToken')
  localStorage.setItem('accessToken', accessToken)
  return accessToken
}
