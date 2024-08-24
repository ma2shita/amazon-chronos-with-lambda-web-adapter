## 単純な時系列データから、次の値を予測する

`demo_seq.csv` を見せる

```shell
python3
```

```python
from chronos import ChronosPipeline
import torch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# (CTRL + L)

### Load CSV
csv = pd.read_csv('demo_seq.csv',header=None)
csv

### 1件推論してみる
pipeline = ChronosPipeline.from_pretrained("amazon/chronos-t5-tiny", device_map="cpu", torch_dtype=torch.bfloat16)
fc = pipeline.predict(torch.tensor(csv[0]), prediction_length=1)
fc
#↑=> 20件の確率予測を得られる。分布なので、中央値が最も確定的（欲しい）情報
np.quantile(fc[0].numpy(), 0.5)

### 10件推論してみる
fc = pipeline.predict(torch.tensor(csv[0]), prediction_length=10) ## SEARCH pred & edit
np.quantile(fc[0].numpy(), 0.5, axis=0) ## HIST & edit
mid = np.quantile(fc[0].numpy(), 0.5, axis=0) ## HIST & edit

### グラフ化してみる
plt.figure(figsize=(7, 5))
plt.plot(csv[0], color="royalblue")
plt.plot(range(29, 29+10), mid, color="tomato")
plt.savefig("fc.png") ## MANUAL

#↓=> 分布であるため、信頼区間も得られる。すなわち、「将来は、この範囲になるはずだ」という情報
np.quantile(fc[0].numpy(), [0.2, 0.5, 0.8], axis=0) ## SEARCH qua & edit
low, mid, high = np.quantile(fc[0].numpy(), [0.2, 0.5, 0.8], axis=0) ## HIST & edit
plt.fill_between(range(29, 29+10), low, high, color="tomato", alpha=0.3)
plt.savefig("fc.png") ## SEARCH save & edit

## EDIT: eg.csv (29 -> 34)

csv = pd.read_csv('demo_seq.csv',header=None) ## SEARCH read
csv
fc = pipeline.predict(torch.tensor(csv[0]), prediction_length=1) ## SEARCH pred & edit
low, high = np.quantile(fc[0].numpy(), [0.2, 0.8]) ## SEARCH quan & edit
low, high ## MANUAL
low < 35 < high ## MANUAL
low < 100 < high ## HIST & edit
```

## Web API 化をしながら、精度を見てみる

`main.py` コード解説

```shell
uvicorn --reload --port 8080 main:app
```

（別ターミナル）

```shell
http -b localhost:8080/
echo '{"historical":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]}' | http -b localhost:8080/forecast.json
echo '{"historical":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]}' | http -b "localhost:8080/forecast.json?prediction_length=10"
echo '{"historical":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]}' | http -b "localhost:8080/forecast.png?prediction_length=10" | img2sixel
#（tiny -> large)
echo '{"historical":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]}' | http -b "localhost:8080/forecast.png?prediction_length=10" | img2sixel
```

## Lambda Web Adapter

* `Dockerfile` 解説
* ECR, Lambda解説
* 実際に実行してみる

EoT
