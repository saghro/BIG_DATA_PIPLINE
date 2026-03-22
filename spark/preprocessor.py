import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, regexp_replace, trim, lower, year, month, dayofmonth, hour, dayofweek, dayofyear, pandas_udf
from pyspark.sql.types import StringType
from pyspark.ml.feature import Tokenizer, StopWordsRemover
import config 

class DataPreprocessor:
    """
    Classe responsable du nettoyage, tokenization, feature engineering et analyse de sentiment.
    """
    
    def clean_text(self, df: DataFrame) -> DataFrame:
        """Nettoyage Regex et formatage basique."""
        df = df.dropna(subset=["text"])
        df = df.withColumn("text", lower(col("text")))
        # Suppression URLs et caractères spéciaux
        df = df.withColumn("text", regexp_replace(col("text"), r"https?://\S+|www\.\S+|[^A-Za-z0-9\s]", ""))
        # Suppression espaces multiples
        df = df.withColumn("text", trim(regexp_replace(col("text"), r"\s+", " ")))
        return df

    def extract_time_features(self, df: DataFrame) -> DataFrame:
        """Extraction des features temporelles."""
        return df.withColumn("datetime", col("timestamp").cast("timestamp")) \
                 .withColumn("year", year("datetime")) \
                 .withColumn("month", month("datetime")) \
                 .withColumn("day", dayofmonth("datetime")) \
                 .withColumn("hour", hour("datetime")) \
                 .withColumn("day_of_week", dayofweek("datetime")) \
                 .withColumn("day_of_year", dayofyear("datetime"))

    def tokenize_and_remove_stopwords(self, df: DataFrame) -> DataFrame:
        """Tokenization NLP."""
        tokenizer = Tokenizer(inputCol="text", outputCol="words")
        df = tokenizer.transform(df)
        
        remover = StopWordsRemover(inputCol="words", outputCol="filtered_words", stopWords=config.STOPWORDS)
        return remover.transform(df)

    # Note: Cette méthode est statique car Spark la sérialise différemment
    @staticmethod
    @pandas_udf(StringType())
    def get_sentiment_udf(series: pd.Series) -> pd.Series:
        """Analyse de sentiment simple basée sur des mots-clés."""
        positive_words = ['bullish', 'moon', 'hodl', 'buy', 'good', 'amazing', 'future', 'great', 'excellent']
        negative_words = ['dip', 'sell', 'crash', 'bad', 'volatile', 'risky', 'terrible', 'worst']
        
        sentiments = []
        for text in series:
            if pd.isna(text):
                sentiments.append('Neutral')
                continue
                
            text_lower = str(text).lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                sentiments.append('Positive')
            elif neg_count > pos_count:
                sentiments.append('Negative')
            else:
                sentiments.append('Neutral')
        
        return pd.Series(sentiments)