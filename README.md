# AAA740-final-project-PoseEverything
Final project for course AAA740 - Special Topics in Artificial Intelligence - Pose for Everything with foundation model Dino


train 
------------------
```python 
python tools/train.py --config ${your config} --work-dir ${folder to save output} --auto-resume ${checkpoint folder}
```
In our experience, training on DinoV2 takes 8-9 hours, but it can vary in data split and your environment.

test 
--------------------
```python
python test.py ${your config} ${checkpoint file}
```

In our experience, evaluation takes 20-30 mins, but it can vary in data split and your environment.



