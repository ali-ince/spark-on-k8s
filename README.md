= Important Links

- Used Docker Desktop's Kubernetes support

- https://spark.apache.org/docs/latest/running-on-kubernetes.html
- https://neo4j.com/docs/operations-manual/current/kubernetes/helm-charts-setup/ (run in default namespace)

Launch neo4j:

```shell
helm repo add neo4j https://helm.neo4j.com/neo4j
helm repo update
helm install my-neo4j-release neo4j/neo4j -f neo4j.yaml
```

Create custom service account:
```shell
kubectl create serviceaccount spark
kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default
```

Create docker image:

```shell
${spark_home}/bin/docker-image-tool.sh -r docker.io/connectors-pyspark -t v3.4.0 -p ${spark_home}/kubernetes/dockerfiles/spark/bindings/python/Dockerfile build
```

Install python3 and configure:
```shell
python3 -m venv venv
python3 -m pip -r requirements.txt
```

Launch a Job:

(`/private/tmp` is probably MacOS specific, you might need to reconfigure it based on your OS/Docker/K8S configuration)

```shell
SOURCE_DIR=/private/tmp/spark-on-k8s
VOLUME_TYPE=hostPath
VOLUME_NAME=spark-on-k8s
MOUNT_PATH=/private/tmp/spark-on-k8s

spark-submit \
  --master k8s://https://kubernetes.docker.internal:6443 \
  --deploy-mode cluster \
  --name spark-test \
  --packages org.neo4j:neo4j-connector-apache-spark_2.12:5.2.0_for_spark_3,org.postgresql:postgresql:42.6.0 \
  --conf spark.kubernetes.file.upload.path=$SOURCE_DIR \
  --conf spark.kubernetes.driver.volumes.$VOLUME_TYPE.$VOLUME_NAME.mount.path=$MOUNT_PATH \
  --conf spark.kubernetes.driver.volumes.$VOLUME_TYPE.$VOLUME_NAME.mount.type=Directory \
  --conf spark.kubernetes.driver.volumes.$VOLUME_TYPE.$VOLUME_NAME.options.path=$MOUNT_PATH \
  --conf spark.kubernetes.executor.volumes.$VOLUME_TYPE.$VOLUME_NAME.mount.path=$MOUNT_PATH \
  --conf spark.kubernetes.executor.volumes.$VOLUME_TYPE.$VOLUME_NAME.mount.type=Directory \
  --conf spark.kubernetes.executor.volumes.$VOLUME_TYPE.$VOLUME_NAME.options.path=$MOUNT_PATH \
  --conf spark.kubernetes.container.image=connectors-pyspark/spark-py:v3.4.0 \
  --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
  --conf spark.driver.extraJavaOptions="-Divy.cache.dir=/tmp -Divy.home=/tmp" \
  push-to-neo4j.py
```