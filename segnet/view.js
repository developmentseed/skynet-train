const qs = require('querystring')
const http = require('choo/http')
const choo = require('choo')
const mapboxgl = require('mapbox-gl')
const tilebelt = require('tilebelt')

const query = qs.parse(window.location.search.substring(1))
const baseurl = query.baseurl || ''

mapboxgl.accessToken = query.access_token
const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/satellite-v8',
  center: [-74.50, 40],
  zoom: 9
})
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
  state: { items: [], limit: 50 },
  subscriptions: [
    function (send) { send('http:get_json') } // grab json data at startup
  ],
  reducers: {
    'setTestOutput': (action, state) => ({ items: action.payload }),
    'loadMore': logged((action, state) => ({ limit: state.limit + 50 }), 'loadMore')
  },
  effects: {
    'error': (state, event) => console.error(`error: ${event.payload}`),
    'print': (state, event) => console.log(`http: ${event.payload}`),
  }
})

app.model({
  namespace: 'http',
  effects: {
    'get_json': getJson
  }
})

const view = (params, state, send) => choo.view`
  <div>
  <ul>
      <li class="header">
        <div>Input Image</div>
        <div>OSM "ground truth"</div>
        <div>Net Prediction</div>
      </li>
      ${state.app.items
      .slice(0, state.app.limit)
      .map(item => choo.view`
           <li data-tile=${getTile(item)} onclick=${onClick}>
           <img src=${getSatelliteTileURL(item)}></img>
           <img src=${baseurl + item.groundtruth}></img>
           <img src=${baseurl + item.prediction}></img>
           </li>
           `)
  }
  </ul>
  ${state.app.limit < state.app.items.length
    ? choo.view`<button onclick=${() => send('app:loadMore')}>Load More</button>`
    : ''}
  </div>
`

app.router((route) => [
  route('/', logged(view, 'view'))
])

document.querySelector('#app').appendChild(app.start())

function getTile (item) {
  var match = /(\d*)-(\d*)-(\d*).png/.exec(item.test_data)
  return match.slice(1, 4)
}
function getSatelliteTileURL(item) {
  var tile = getTile(item)
  return 'http://b.tiles.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png'
    .replace('{z}', tile[0])
    .replace('{x}', tile[1])
    .replace('{y}', tile[2]) +
    '?access_token=' + query.access_token
}

function onClick (event) {
  var tile = event.currentTarget.dataset.tile.split(',').map(Number)
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
      coordinates: [ coordinates.concat([[w,n]]) ]
    }
  })

  var gt = event.currentTarget.querySelector('img:last-child')
  showOverlay(gt.src, coordinates)
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
      return send('app:error', { payload:'something went wrong' })
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
