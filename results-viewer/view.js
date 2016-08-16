const qs = require('querystring')
const url = require('url')
const http = require('choo/http')
const choo = require('choo')
const tilebelt = require('tilebelt')
const createMap = require('./map')
const getSatelliteTileURL = require('./get-tile-url')

const query = qs.parse(window.location.search.substring(1))
const baseurl = query.baseurl || ''

let map = createMap(query)
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
  state: { metrics: {}, items: [], limit: 50, sort: 'completeness_score:descending' },
  subscriptions: [
    function (send) { send('http:get_json') } // grab json data at startup
  ],
  reducers: {
    'setTestOutput': (action, state) => {
      return {
        items: action.payload.images,
        metrics: {
          correctness: action.payload.correctness,
          completeness: action.payload.completeness
        }
      }
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
  const sort = state.app.sort.split(':')
  const items = state.app.items
  .filter(function (item) {
    return item.metrics[sort[0]] >= 0
  })
  .sort(function (a, b) {
    var diff = a.metrics[sort[0]] - b.metrics[sort[0]]
    return sort[1] === 'ascending' ? diff : -diff
  })

  let correctness = 0
  let completeness = 0
  if (state.app.metrics.correctness) {
    correctness = state.app.metrics.correctness
    completeness = state.app.metrics.completeness
  }

  const imgStyle = query.compare ? 'width: 24%' : 'width: 32%'

  return choo.view`
    <div>
    <dl>
      <dt>Total Correctness:</dt>
      <dd>${correctness.toFixed(3)}</dd>
      <dt>Total Completeness:</dt>
      <dd>${completeness.toFixed(3)}</dd>
    </dl>
    <button onclick=${() => send('app:sort', { key: 'correctness_score:descending' })}>Most Correct</button>
    <button onclick=${() => send('app:sort', { key: 'correctness_score:ascending' })}>Least Correct</button>
    <button onclick=${() => send('app:sort', { key: 'completeness_score:descending' })}>Most Complete</button>
    <button onclick=${() => send('app:sort', { key: 'completeness_score:ascending' })}>Least Complete</button>
    <ul>
        <li class="header">
          <div>Input Image</div>
          <div>OSM "ground truth"</div>
          <div>Net Prediction</div>
        </li>
        ${items
        .slice(0, state.app.limit)
        .map(item => {
          var tile = getTile(item)
          var image = getSatelliteTileURL(query, tile[0], tile[1], tile[2])
          return choo.view`
             <li data-tile=${getTile(item)}>
                 <img style=${imgStyle} src=${image} onclick=${onClick}></img>
                 <img style=${imgStyle} src=${baseurl + item.groundtruth} onclick=${onClick}></img>
                 <img style=${imgStyle} src=${baseurl + item.prediction} onclick=${onClick}></img>
                 ${query.compare ? choo.view`
                   <img style=${imgStyle} src=${url.resolve(baseurl, query.compare + '/' + item.prediction)} onclick=${onClick}></img>
                   ` : ''}
                 <div>
                  Completeness: ${item.metrics.completeness_score.toFixed(3)}
                  Correctness: ${item.metrics.correctness_score.toFixed(3)}
                 </div>
             </li>
             `
        })
    }
    </ul>
    ${state.app.limit < state.app.items.length
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
  return match.slice(1, 4)
}

function onClick (event) {
  var tile = event.currentTarget.parentNode.dataset.tile.split(',').map(Number)
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

  map.on('render', addImageLayer)
  function addImageLayer () {
    if (map.getSource('class-overlay').loaded()) {
      map.off('render', addImageLayer)
      map.addLayer({
        'id': 'class-overlay',
        'source': 'class-overlay',
        'type': 'raster',
        'paint': { 'raster-opacity': 0.5 }
      })
    }
  }
}

function getJson (state, action, send) {
  console.log('getJson', state, action)
  http.get(baseurl + 'index.json', { json: true }, function (err, res, body) {
    if (err) return send('app:error', { payload: err.message })
    if (res.statusCode !== 200 || !body) {
      return send('app:error', { payload: 'something went wrong' })
    }
    if (typeof body === 'string') {
      body = JSON.parse(body.replace(/NaN/g, '-1'))
    }
    send('app:setTestOutput', { payload: body })
  })
}

function logged (view, tag) {
  return function () {
    console.log(tag || '', arguments)
    return view.apply(this, Array.prototype.slice.call(arguments))
  }
}

