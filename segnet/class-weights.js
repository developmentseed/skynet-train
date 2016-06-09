var fs = require('fs')
var data = fs.readFileSync(process.argv[2], 'utf-8').split('\n')
	.slice(1)
	.filter(Boolean)
	.map(x => x.split(',').map(Number))

var frequencies = data.map(x => x[1] / (x[2] * 65536))

var sorted = [].concat(frequencies).sort((a, b) => (a - b))
var n = sorted.length
var median = n % 2 === 0 ? (sorted[n / 2] + sorted[n / 2 - 1]) / 2 : sorted[n / 2 - 0.5]

console.log('frequencies', frequencies)
console.log('median', median)
console.log(frequencies.map(x => (median / x)).join('\n'))
