const http = require('choo/http')
const choo = require('choo')

const app = choo()

app.model({
  namespace: 'app',
  state: { items: [] },
  subscriptions: [
    function (send) { send('http:get_json') } // grab json data at startup
  ],
  reducers: {
    'setTestOutput': (action, state) => ({ items: action.payload })
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
  ${state.app.items
    .map(item => choo.view`
         <div>
           <img src=${item.input}></img>
           <img src=${item.groundtruth}></img>
           <img src=${item.prediction}></img>
         </div>
    `)
  }
  </main>
`

app.router((route) => [
  route('/', view)
])

document.body.appendChild(app.start())

function getJson (state, action, send) {
  console.log('getJson', state, action)
  http.get('index.json', { json: true }, function (err, res, body) {
    if (err) return send('app:error', { payload: err.message })
    if (res.statusCode !== 200 || !body) {
      return send('app:error', { payload:'something went wrong' })
    }
    send('app:setTestOutput', { payload: body })
  })
}
