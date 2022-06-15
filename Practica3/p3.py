from pyspark import SparkContext, SparkConf, SQLContext
from pyspark import SparkContext, SparkConf, sql
from pyspark.ml import Pipeline
from pyspark.ml.classification import DecisionTreeClassifier, LinearSVC, RandomForestClassifier
from pyspark.ml.feature import IndexToString, StringIndexer, VectorIndexer
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.feature import OneHotEncoder

# Conectar y configurar Spark
conf = SparkConf().setAppName("Practica3")
sc = SparkContext(conf = conf)
sqlContext = SQLContext(sc)

# Leer conjunto de datos
df = sqlContext.read.csv("/FileStore/tables/datos.csv", sep=",", header=True, inferSchema=True)

## PREPARACIÓN DE LOS DATOS

# Eliminar datos perdidos, si los hubiese
df = df.na.drop()

# Coger todas las columnas menos la última (clase) y considerarlas como características (features)
# Antes hay que indexarlas para que las acepte
columna10index = StringIndexer(inputCol="Columna10", outputCol="Columna10Index")
df = columna10index.fit(df).transform(df)
df = OneHotEncoder(inputCol="Columna10Index", outputCol="Columna10_vec").fit(df).transform(df)
columna33index = StringIndexer(inputCol="Columna33", outputCol="Columna33Index")
df = columna33index.fit(df).transform(df)
df = OneHotEncoder(inputCol="Columna33Index", outputCol="Columna33_vec").fit(df).transform(df)
columna41index = StringIndexer(inputCol="Columna41", outputCol="Columna41Index")
df = columna41index.fit(df).transform(df)
df = OneHotEncoder(inputCol="Columna41Index", outputCol="Columna41_vec").fit(df).transform(df)
columna51index = StringIndexer(inputCol="Columna51", outputCol="Columna51Index")
df = columna51index.fit(df).transform(df)
df = OneHotEncoder(inputCol="Columna51Index", outputCol="Columna51_vec").fit(df).transform(df)
columna69index = StringIndexer(inputCol="Columna69", outputCol="Columna69Index")
df = columna69index.fit(df).transform(df)
df = OneHotEncoder(inputCol="Columna69Index", outputCol="Columna69_vec").fit(df).transform(df)
columna74index = StringIndexer(inputCol="Columna74", outputCol="Columna74Index")
df = columna74index.fit(df).transform(df)
df = OneHotEncoder(inputCol="Columna74Index", outputCol="Columna74_vec").fit(df).transform(df)
columna78index = StringIndexer(inputCol="Columna78", outputCol="Columna78Index")
df = columna78index.fit(df).transform(df)
df = OneHotEncoder(inputCol="Columna78Index", outputCol="Columna78_vec").fit(df).transform(df)
inputCols = [
    'Columna10_vec',
    'Columna33_vec',
    'Columna41_vec',
    'Columna51_vec',
    'Columna69_vec',
    'Columna74_vec',
    'Columna78_vec',
]
assembler = VectorAssembler(inputCols=inputCols, outputCol="features")
df = assembler.transform(df)
featureIndexer = VectorIndexer(inputCol="features", outputCol="indexedFeatures", maxCategories=4).fit(df)

# Indexar la etiqueta de clase llamandola label
df = df.withColumnRenamed("clase", "label")
labelIndexer = StringIndexer(inputCol="label", outputCol="indexedLabel").fit(df)

# Comprobar cual de las dos clases es la mayoritaria, y hacerle undersampling a esa
clase1 = df.filter("label = 1")
clase0 = df.filter("label = 0")
if clase1.count() > clase0.count():
    under = clase1.sample(withReplacement=False, fraction=1.0, seed=0).limit(clase0.count())
    df = under.union(clase0)
else:
    under = clase0.sample(withReplacement=False, fraction=1.0, seed=0).limit(clase1.count())
    df = under.union(clase1)
    
# Dividir datos en conjunto de entrenamiento (80%) y prueba (20%)
(trainingData, testData) = df.randomSplit([0.8, 0.2])

## MODELO DE ÁRBOL DE DECISIÓN 1
dt = DecisionTreeClassifier(labelCol="indexedLabel", featuresCol="indexedFeatures", maxDepth=10, maxBins=32)
pipeline = Pipeline(stages=[labelIndexer, featureIndexer, dt])
model = pipeline.fit(trainingData) # Entrenamiento
predictions = model.transform(testData) # Predicciones a partir del modelo entrenado
evaluator = MulticlassClassificationEvaluator(labelCol="indexedLabel", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("ÁRBOL DE DECISIÓN 1 - Error = %g " % (1.0 - accuracy))

## MODELO DE ÁRBOL DE DECISIÓN 2
dt = DecisionTreeClassifier(labelCol="indexedLabel", featuresCol="indexedFeatures", maxDepth=15, maxBins=64)
pipeline = Pipeline(stages=[labelIndexer, featureIndexer, dt])
model = pipeline.fit(trainingData) # Entrenamiento
predictions = model.transform(testData) # Predicciones a partir del modelo entrenado
evaluator = MulticlassClassificationEvaluator(labelCol="indexedLabel", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("ÁRBOL DE DECISIÓN 2 - Error = %g " % (1.0 - accuracy))

## MODELO DE SVM 1
lsvc = LinearSVC(maxIter=10, regParam=0.1)
lsvcModel = lsvc.fit(trainingData)
evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
pred = lsvc.transform(testData)
acc = evaluator.evaluate(pred)
print("SVM 1 - Error = %g " % (1.0 - acc))

## MODELO DE SVM 2
lsvc = LinearSVC(maxIter=20, regParam=0.5)
lsvcModel = lsvc.fit(trainingData)
evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
pred = lsvc.transform(testData)
acc = evaluator.evaluate(pred)
print("SVM 2 - Error = %g " % (1.0 - acc))


## MODELO DE RANDOM FOREST 1
rf = RandomForestClassifier(labelCol="indexedLabel", featuresCol="indexedFeatures", numTrees=10, maxDepth=10)
labelConverter = IndexToString(inputCol="prediction", outputCol="predictedLabel", labels=labelIndexer.labels)
pipeline = Pipeline(stages=[labelIndexer, featureIndexer, rf, labelConverter])
model = pipeline.fit(trainingData)
predictions = model.transform(testData)
evaluator = MulticlassClassificationEvaluator(labelCol="indexedLabel", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("RANDOM FOREST 1 - Error %g" % (1.0 - accuracy))

## MODELO DE RANDOM FOREST 2
rf = RandomForestClassifier(labelCol="indexedLabel", featuresCol="indexedFeatures", numTrees=15, maxDepth=15)
labelConverter = IndexToString(inputCol="prediction", outputCol="predictedLabel", labels=labelIndexer.labels)
pipeline = Pipeline(stages=[labelIndexer, featureIndexer, rf, labelConverter])
model = pipeline.fit(trainingData)
predictions = model.transform(testData)
evaluator = MulticlassClassificationEvaluator(labelCol="indexedLabel", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("RANDOM FOREST 2 - Error %g" % (1.0 - accuracy))
    