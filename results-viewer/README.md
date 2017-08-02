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
