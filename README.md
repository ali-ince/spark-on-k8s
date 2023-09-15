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

Launch a Job:
```shell
spark-submit \
  --master k8s://https://kubernetes.docker.internal:6443 \
  --deploy-mode cluster \
  --name spark-test \
  --conf spark.kubernetes.container.image=connectors-pyspark/spark-py:v3.4.0 \
  --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
  --conf spark.jars=https://github.com/neo4j-contrib/neo4j-spark-connector/releases/download/5.1.0/neo4j-connector-apache-spark_2.12-5.1.0_for_spark_3.jar \
  https://raw.githubusercontent.com/ali-ince/spark-on-k8s/main/push-to-neo4j.py
```