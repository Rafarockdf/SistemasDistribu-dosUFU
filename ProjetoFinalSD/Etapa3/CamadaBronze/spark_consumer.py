from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

spark = SparkSession.builder \
    .appName("KafkaCidades") \
    .getOrCreate()

# Define o schema da mensagem
schema = StructType([
    StructField("tipo", StringType(), True),
    StructField("payload", StructType([
        StructField("id", IntegerType(), True),
        StructField("cidade", StringType(), True),
        StructField("estado", StringType(), True),
        StructField("lat", DoubleType(), True),
        StructField("lon", DoubleType(), True)
    ]), True)
])

# Ler do Kafka
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "cidades_raw") \
    .load()

# Converter de bytes para string e aplicar schema
df_str = df.selectExpr("CAST(value AS STRING) as json")
df_json = df_str.select(from_json(col("json"), schema).alias("data"))
df_final = df_json.select("data.payload.*")  # só os campos do payload

# Mostrar no console
query = df_final.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()
