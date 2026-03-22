import sqlite3
import pandas as pd

# Database connect karo
conn = sqlite3.connect("parking.db")

# History table se data uthao
df = pd.read_sql_query("SELECT slot, status, day, timestamp FROM history", conn)

conn.close()

print(df.head())   # Verify karo ki data aa raha hai

# 👉 Feature Engineering yahan start karo
# Day ko number mein convert karo
df['day_num'] = df['day'].astype('category').cat.codes

# Timestamp se hour nikalna
df['hour'] = pd.to_datetime(df['timestamp']).dt.hour

# Hour ko time slots mein convert karna
df['time_slot'] = pd.cut(df['hour'],
                         bins=[0,6,12,18,24],
                         labels=['Night','Morning','Afternoon','Evening'],
                         right=False)

# Time slot ko number mein convert karna
df['time_num'] = df['time_slot'].astype('category').cat.codes

print(df.head())   # Verify karo ki naye columns aa gaye
X = df[['day_num', 'time_num']]
y = df['status']
print(X.head())
print(y.head())

from sklearn.model_selection import train_test_split

# Data ko training aur testing mein divide karo
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

print("Training set size:", len(X_train))
print("Testing set size:", len(X_test))
from sklearn.tree import DecisionTreeClassifier

# Model initialize karo
model = DecisionTreeClassifier()

# Model train karo
model.fit(X_train, y_train)

# Accuracy check karo
print("Accuracy:", model.score(X_test, y_test))

import pickle

# Model ko pickle file mein save karo
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
