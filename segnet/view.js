const http = require('choo/http')
const choo = require('choo')
const qs = require('querystring')

var query = qs.parse(window.location.search.substring(1))
var baseurl = query.baseurl || ''

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
  <main>
  <ul class='results'>
      ${state.app.items
      .slice(0, state.app.limit)
      .map(item => choo.view`
           <li>
           <img style='width: 33%' src=${getSatelliteTileURL(item)}></img>
           <img style='width: 33%' src=${baseurl + item.groundtruth}></img>
           <img style='width: 33%' src=${baseurl + item.prediction}></img>
           </li>
           `)
  }
  </ul>
  ${state.app.limit < state.app.items.length
    ? choo.view`<button onclick=${() => send('app:loadMore')}>Load More</button>`
    : ''}
  </main>
`

app.router((route) => [
  route('/', logged(view, 'view'))
])

document.body.appendChild(app.start())

function getSatelliteTileURL(item) {
  var match = /(\d*)-(\d*)-(\d*).png/.exec(item.test_data)
  console.log(match)
  return 'http://b.tiles.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png'
    .replace('{z}', match[1])
    .replace('{x}', match[2])
    .replace('{y}', match[3]) +
    '?access_token=' + query.access_token
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
