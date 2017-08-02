In addition to the usage shown in the main [README](https://github.com/developmentseed/skynet-train#quick-start), this viewer can also be used as a standalone tool. The only requirement is that an `index.json` file be added to the `dist` folder with the following format:

```js
{
  "images": [
    {
      "index": 0,
      "prediction": "0_prediction.png", // location of prediction image
      "metrics": {
        "correctness_score": 0.43474827245804543,
        "completeness_score": 0.79609929078014185 
      },
      "groundtruth": "0_groundtruth.png", // location of label image ("groundtruth")
      "input": "0_input.png" // location of input image (satellite imagery in this case)
    },
    ...
  ]
}
```

The `dist` folder can be served with [your preferred command](https://gist.github.com/willurd/5720255) and you can access the results at `http://localhost:8000/view.html?access_token=your_access_token`
