create an ec2 instance with the deep learning ami
copy the contents of this folder into /home/ec2-user/src

run
```bash
cd /home/ec2-user
export AWS_SECRET_ACCESS_KEY="<YourAccessKey>"
export AWS_ACCESS_KEY_ID="<YourID>"
aws s3 cp s3://ds-skynet/dg-goma-2 ./.keras/datasets/dg-goma-2 --recursive
aws s3 cp s3://ds-skynet/models/dg-goma-2-tuning/model-h5s ./.keras/models --recursive
sudo pip install keras --upgrade
sudo pip install git+https://www.github.com/farizrahman4u/keras-contrib.git
cd src
python convert_to_voc.py
```

Then, ```aws configure``` and set the default region to ```us-east-1```

Populate the SQS queue hyperparameters.fifo with whatever hyperparameter jsons you want to train on.

Start training with ```nohup python train.py &```