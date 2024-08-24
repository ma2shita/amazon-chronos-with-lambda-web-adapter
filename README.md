# Deploying Amazon Chronos Using Lambda Web Adapter

This repository provides a simple guide to deploying Amazon Chronos, a time-series database, using AWS Lambda Web Adapter. By using Lambda, you can run Chronos without worrying about servers. This setup is cost-effective and scales automatically, making it easier to manage your time-series data in the cloud.

Key Dependencies:

* Amazon Chronos: https://www.amazon.science/code-and-datasets/chronos-learning-the-language-of-time-series
* Lambda Web Adapter: https://github.com/awslabs/aws-lambda-web-adapter
  * Docker: https://www.docker.com/
  * FastAPI: https://fastapi.tiangolo.com/

Other references:

* Overview: [Get the Future by Chronos of Amazon's Timeseries FM](https://speakerdeck.com/ma2shita/get-the-future-by-chronos-of-amazons-time-series-fm)

## Files

* `main.py`: Implementation Using Chronos and Example with FastAPI
* `test_main.py`: Testing FastAPI with Pytest
* `live-demo-scripts.md`: Cheat Sheet for Live Demo
* `demo_seq.csv`: Time-series data for demo

## Getting Started / Local Development

Prepare:

* Python3 (3.12 or above)
* Docker (CE 27.1 or above)

```shell
git clone https://github.com/ma2shita/amazon-chronos-with-lambda-web-adapter
cd amazon-chronos-with-lambda-web-adapter
python3 -m venv chronos-libs
source chronos-libs/bin/activate
pip install -U pip
pip install "huggingface_hub[cli]"
pip install git+https://github.com/amazon-science/chronos-forecasting.git
pip install uvicorn fastapi pandas matplotlib
pip install pytest httpx
huggingface-cli download amazon/chronos-t5-tiny
pytest test_main.py
#=> Congrats! You can edit `main.py` and `test_main.py`.
uvicorn --reload --port=8080 main:app
#=> curl localhost:8080
#=> curl -X POST -H "Content-Type:application/json" -d '{"historical":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]}' localhost:8080/forecast.json
```

### Continuation

```shell
cd amazon-chronos-with-lambda-web-adapter
source chronos-libs/bin/activate
pytest test_main.py
```

## Build container then push to Amazon ECR

```shell
## Prepare
aws ecr create-repository --repository-name ${REPO_NAME} # Can be made in the management console.
```

```shell
## Build
docker buildx build --target prod_runner .
#=> You can enter container: `docker run -it --rm ${NEW_IMAGE_ID_AND_TAG} /bin/bash`
docker tag ${NEW_IMAGE_ID_AND_TAG} ${ECR_URL_AND_TAG}
aws ecr get-login-password | docker login --username AWS --password-stdin ${ACCOUNTID}.dkr.ecr.${REGION}.amazonaws.com
docker push ${ECR_URL_AND_TAG}
## NEXT: Create or Update a Lambda function based on this container
```

```shell
## Tips: Update a Lambda function via AWS CLI
aws lambda update-function-code --function-name ${MY-FUNCTION} --image-uri ${ECR_URI}
while true ; do aws lambda get-function --function-name amazon-chronos-t5-tiny_fastapi0 | jq -r .Configuration.LastUpdateStatus ; sleep 5 ; done
# waiting for `Successful`
```

## References

Chronos

* [Chronos: Learning the language of time series](https://www.amazon.science/code-and-datasets/chronos-learning-the-language-of-time-series)
  * [amazon-science/chronos-forecasting](https://github.com/amazon-science/chronos-forecasting)
* [Google Colabで時系列基盤モデルを試す](https://note.com/hatti8/n/n9e9221c8d1ca)

Tools and Developments

* huggingface
  * [Manage huggingface_hub cache-system](https://huggingface.co/docs/huggingface_hub/guides/manage-cache) Learn the Cache system on Huggingface
  * [Command Line Interface (CLI)](https://huggingface.co/docs/huggingface_hub/main/en/guides/cli) huggingface-cli
* Amazon ECR and Lambda Web Adapter
  * [docker/library/python](https://gallery.ecr.aws/docker/library/python)
  * [awsguru/aws-lambda-adapter](https://gallery.ecr.aws/awsguru/aws-lambda-adapter)
  * [SinatraをAWS Lambdaで動かす (Lambda Web Adapter 0.8.1 使用)](https://qiita.com/ma2shita/items/55a655d7781fc2e72fd7) Step by Step for Lambda Web Adapter (It's own content)
* Docker
  * [マルチステージビルドの利用](https://matsuand.github.io/docs.docker.jp.onthefly/develop/develop-images/multistage-build/) Multi-stage build for Docker
  * [JSONArgsRecommended](https://docs.docker.com/reference/build-checks/json-args-recommended/) Learn the CMD, ENTRYPOINT
* FastAPI
  * [FastAPI](https://fastapi.tiangolo.com/ja/)

## Author

This project is maintained by Kohei "Max" MATSUSHITA.  
If you have any questions or suggestions, feel free to reach out via GitHub.

## Contributing

We welcome contributions to this project! Here’s how you can help:

1. **Bug Reports**: If you encounter any issues or bugs, please feel free to submit a bug report. We appreciate your help in making this project better.
2. **Pull Requests**: You can directly create a pull request to contribute code or features. There’s no need to create an issue first unless you want to discuss the changes before starting.
3. **Coding Style**: There is no specific coding style required. Just make sure your code is clear and well-structured.
4. **Testing**: Please ensure that your code is tested before submitting a pull request. This helps maintain the stability and reliability of the project.
5. **Documentation**: There are no specific documentation requirements. Feel free to add documentation if you think it’s necessary, but it’s not required.
6. **Review and Merge Process**: We follow a simple pull request and merge process. Your contributions will be reviewed and merged if everything looks good.

Thank you for your contributions!

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

EoT
