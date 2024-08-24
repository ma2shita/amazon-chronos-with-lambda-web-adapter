from chronos import ChronosPipeline
import torch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from fastapi import FastAPI, Query
from starlette.responses import StreamingResponse

def forecast(historical: pd.DataFrame, prediction_length: int = 1) -> pd.DataFrame:
    pl = ChronosPipeline.from_pretrained("amazon/chronos-t5-tiny", device_map="cpu", torch_dtype=torch.bfloat16)
    fc = pl.predict(torch.tensor(historical[0]), num_samples=len(historical), prediction_length=prediction_length)
    min, median, max = np.quantile(fc[0].numpy(), [0.20, 0.50, 0.80], axis=0) # 20%, 50%, 80%
    ret = pd.DataFrame({"min": min, "median": median, "max": max})
    return ret

app = FastAPI()

@app.get("/")
def readness_check_from_lambda_web_adapter():
    return {"status": "OK"}

from pydantic import BaseModel
from typing import List
class Payload(BaseModel):
    historical: List

@app.post("/forecast.json")
def forecast_ret_json(payload: Payload, prediction_length: int = 1):
    # NOTE: need validator for input data
    data = pd.DataFrame(payload.historical)
    fc = forecast(historical=data, prediction_length=prediction_length)
    # formatting for output
    ret = {"forecast": fc.to_dict(orient="list")}
    return ret

@app.post("/forecast.png")
def forecast_ret_png(payload: Payload, prediction_length: int = 10):
    # NOTE: need validator for input data
    data = pd.DataFrame(payload.historical) # TODO: need validator for input data
    fc = forecast(historical=data, prediction_length=prediction_length)
    # formatting for output
    plt.figure(figsize=(5, 3))
    plt.plot(data, color="royalblue", label="historical data")
    _forecast_plot_area = range(len(data), len(data)+len(fc["median"]))
    plt.plot(_forecast_plot_area, fc["median"], color="tomato", label="median(50%) forecast")
    plt.fill_between(_forecast_plot_area, fc["min"], fc["max"], color="tomato", alpha=0.3, label="20%-80% prediction")
    plt.legend()
    fd = io.BytesIO()
    plt.savefig(fd, format="png")
    fd.seek(0)
    ret = StreamingResponse(fd, media_type="image/png")
    return ret

if __name__ == '__main__':
    data = pd.read_csv('demo_seq.csv',header=None)
    fc = forecast(historical=data, prediction_length=1)
    print(fc)
