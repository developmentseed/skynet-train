const qs = require('querystring')
const http = require('choo/http')
const choo = require('choo')
const tilebelt = require('tilebelt')
const createMap = require('./map')
const getSatelliteTileURL = require('./get-tile-url')

const query = qs.parse(window.location.search.substring(1))
const accessToken = require('./access-token')(query)
let baseurls = query.baseurl || ''
if (!Array.isArray(baseurls)) { baseurls = [baseurls] }
// add trailing slash
baseurls = baseurls.map(b => (b === '' || b.endsWith('/')) ? b : `${b}/`)

let map = accessToken && !query.hasOwnProperty('no-map') && createMap(query)
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

const app = choo()

app.model({
  namespace: 'app',
  state: { results: [], limit: 50, sort: 'index' },
  subscriptions: [
    function (send) { send('http:get_json') } // grab json data at startup
  ],
  reducers: {
    'setTestOutput': (action, state) => {
      return Object.assign({}, state, {
        results: state.results.concat({
          baseurl: action.payload.baseurl,
          items: action.payload.images,
          metrics: {
            correctness: action.payload.correctness,
            completeness: action.payload.completeness
          }
        })
      })
    },
    'loadMore': logged((action, state) => ({ limit: state.limit + 50 }), 'loadMore'),
    'sort': (action, state) => ({ sort: action.key })
  },
  effects: {
    'error': (state, event) => console.error(`error: ${event.payload}`),
    'print': (state, event) => console.log(`http: ${event.payload}`)
  }
})

app.model({
  namespace: 'http',
  effects: {
    'get_json': getJson
  }
})

const view = (params, state, send) => {
  const results = [].concat(state.app.results)
    .sort((r, s) => baseurls.indexOf(r.baseurl) - baseurls.indexOf(s.baseurl))

  const sort = state.app.sort.split(':')
  let items
  if (!results.length) {
    items = []
  } else if (sort[0] === 'index') {
    items = [].concat(results[0].items)
  } else {
    items = results[0].items
    .filter(function (item) {
      return item.metrics[sort[0]] >= 0
    })
    .sort(function (a, b) {
      var diff = a.metrics[sort[0]] - b.metrics[sort[0]]
      return sort[1] === 'ascending' ? diff : -diff
    })
  }

  const resultNames = stripCommon(results.map(r => r.baseurl))

  const colCount = 2 + baseurls.length
  const colMargin = 2
  const colStyle = [
    `width: calc(${100 / colCount}% - ${colMargin * colCount}px)`,
    `margin-left: ${colMargin}px`
  ].join('; ')

  let missingAccessToken = ''
  if (!query.hasOwnProperty('no-map') && !accessToken) {
    const url = window.location.href.replace(/#.*$/, '')
    missingAccessToken = choo.view`
    <div class='warning'>
      To view results on the map, add a Mapbox access token to the URL like so:
      ${url}${/\?/.test(url) ? '&' : '?'}access_token=ACCESSTOKEN
    </div>`
  }

  return choo.view`
    <div>
    <button onclick=${() => send('app:sort', { key: 'correctness_score:descending' })}>Most Correct</button>
    <button onclick=${() => send('app:sort', { key: 'correctness_score:ascending' })}>Least Correct</button>
    <button onclick=${() => send('app:sort', { key: 'completeness_score:descending' })}>Most Complete</button>
    <button onclick=${() => send('app:sort', { key: 'completeness_score:ascending' })}>Least Complete</button>
    <button onclick=${() => send('app:sort', { key: 'index' })}>Reset</button>
    ${missingAccessToken}
    <ul class=${map ? 'sidebar' : ''}>
        <li class="header">
          <div style=${colStyle}>Input Image</div>
          <div style=${colStyle}>OSM "ground truth"</div>
          ${results.map((result, i) => {
            return choo.view`
               <div style=${colStyle}>
                 ${resultNames[i]}<br>
                 <div class='metrics'>
                   <nobr>Correct: ${result.metrics.correctness.toFixed(3)}</nobr><br>
                   <nobr>Complete: ${result.metrics.completeness.toFixed(3)}</nobr><br>
                 </div>
               </div>`
          })}
        </li>
        ${items
        .slice(0, state.app.limit)
        .map(item => {
          var tile = getTile(item)
          var image = tile ? getSatelliteTileURL(query, tile[0], tile[1], tile[2])
            : (baseurls[0] + item.input)
          return choo.view`
             <li data-tile=${getTile(item)}>
                 <div style=${colStyle} class="image-input">
                   <img src=${image} onclick=${onClick}></img>
                 </div>
                 <div style=${colStyle} class="image-groundtruth">
                   <img src=${baseurls[0] + item.groundtruth} onclick=${onClick}></img>
                 </div>
                 ${results.map(result => {
                   const it = result.items.find(i => tile.join('') === getTile(i).join(''))
                   return choo.view`
                      <div style=${colStyle} class="image-prediction">
                        <img src=${result.baseurl + it.prediction} onclick=${onClick}></img>
                        <div class="metrics">
                         <nobr>Complete: ${it.metrics.completeness_score.toFixed(3)}</nobr>
                         <nobr>Correct: ${it.metrics.correctness_score.toFixed(3)}</nobr>
                        </div>
                      </div>`
                 })}
             </li>
             `
        })
    }
    </ul>
    ${state.app.limit < items.length
      ? choo.view`<button onclick=${() => send('app:loadMore')}>Load More</button>`
      : ''}
    </div>
  `
}

app.router((route) => [
  route('/', logged(view, 'view'))
])

document.querySelector('#app').appendChild(app.start())

function getTile (item) {
  var match = /(\d*)-(\d*)-(\d*).png/.exec(item.test_data)
  return match && match.slice(1, 4)
}

function onClick (event) {
  if (!map) { return }

  let node = event.currentTarget
  while (node && !(node.dataset && node.dataset.tile)) {
    if (node.parentNode === node) { break }
    node = node.parentNode
  }

  var tile = node.dataset.tile.split(',').map(Number)
  tile = [tile[1], tile[2], tile[0]]
  var [w, s, e, n] = tilebelt.tileToBBOX(tile)
  var z = +tile[2]

  var coordinates = [
    [w, n],
    [e, n],
    [e, s],
    [w, s]
  ]

  map.jumpTo({center: [ (w + e) / 2, (s + n) / 2 ], zoom: z - 1, speed: 2})
  map.getSource('tile').setData({
    type: 'Feature',
    properties: {},
    geometry: {
      type: 'Polygon',
      coordinates: [ coordinates.concat([[w, n]]) ]
    }
  })

  showOverlay(event.currentTarget.src, coordinates)
}

function showOverlay (url, coords) {
  console.log('show overlay', url, coords)
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

  map.addLayer({
    'id': 'class-overlay',
    'source': 'class-overlay',
    'type': 'raster',
    'paint': { 'raster-opacity': 0.5 }
  })
}

function getJson (state, action, send) {
  baseurls.forEach((baseurl, i) => {
    http.get(baseurl + 'index.json', { json: true }, function (err, res, body) {
      if (err) return send('app:error', { payload: err.message })
      if (res.statusCode !== 200 || !body) {
        return send('app:error', { payload: 'something went wrong' })
      }
      if (typeof body === 'string') {
        body = JSON.parse(body.replace(/NaN/g, '-1'))
      }
      body.baseurl = baseurl
      send('app:setTestOutput', { payload: body })
    })
  })
}

function logged (view, tag) {
  return function () {
    console.log(tag || '', arguments)
    return view.apply(this, Array.prototype.slice.call(arguments))
  }
}

/**
 * Given an array of strings, return a new array wherein the common prefix
 * and common postfix for the given strings is removed.
 *
 * Example: stripCommon(['abcHello Worldxyz', 'abc123xyz', 'abcxyz']) ===
 * ['Hello World', '123', '']
 *
 * One small exception: do only treat numerical digits (and "K") as 'common'
 * if the whole string of them is common -- otherwise
 * ['abc_123_5000', 'abc_123_55000'] would become ['', '5'], whereas we really
 * want ['5000', '55000']
 */
function stripCommon (strings) {
  if (!strings.length) return []
  let digits = []
  let pre = 0
  while (pre < strings[0].length) {
    let chars = strings.map(s => s.charAt(pre))
    if (chars.some(c => !c)) { break }
    if (chars.some(c => c !== chars[0])) {
      break
    }
    if (/[\dK]/.test(chars[0])) {
      digits.push(chars[0])
    } else {
      digits = []
    }
    pre++
  }
  console.log(digits)
  strings = strings.map(s => digits.join('') + s.slice(Math.max(pre, 0)))

  let post = 0
  digits = []
  while (post < strings[0].length) {
    let chars = strings.map(s => s.charAt(s.length - post - 1))
    if (chars.some(c => !c.length)) { break }
    if (chars.some(c => c !== chars[0])) {
      break
    }
    if (/[\dK]/.test(chars[0])) {
      digits.unshift(chars[0])
    } else {
      digits = []
    }
    post++
  }
  return strings.map(s => s.slice(0, s.length - post) + digits.join(''))
}

