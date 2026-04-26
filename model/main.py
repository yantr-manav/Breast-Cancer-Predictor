import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def get_clean_data():
    data = pd.read_csv("./data/data.csv")
    
    data = data.drop(['Unnamed: 32', 'id'], axis=1)
    # Use replace instead of map for better pandas compatibility
    data['diagnosis'] = data['diagnosis'].replace({'M': 1, 'B': 0})
    return data

def create_model(data):
    X = data.drop(['diagnosis'], axis=1)
    Y = data['diagnosis']
    
    # Scaling the data
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Split the data
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    
    # Train the model
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(x_train, y_train)
    
    # Test the model
    y_pred = model.predict(x_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy of our model is:", accuracy)
    print("Classification report:\n", classification_report(y_test, y_pred))
    
    return model, scaler
    

def main():
    try:
        data = get_clean_data()
        model, scaler = create_model(data)

        # Create model directory if it doesn't exist
        os.makedirs('model', exist_ok=True)
        
        # Use joblib for better ML model serialization
        joblib.dump(model, 'model/model.pkl')
        joblib.dump(scaler, 'model/scaler.pkl')
        
        print("Model and scaler saved successfully!")
    except Exception as e:
        print(f"Error during model creation and saving: {e}")
        raise

    
if __name__ == '__main__':
    main()