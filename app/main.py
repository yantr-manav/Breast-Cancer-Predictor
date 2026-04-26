import streamlit as st
import joblib
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

def get_clean_data():
    data = pd.read_csv("./data/data.csv")
    
    data = data.drop(['Unnamed: 32', 'id'], axis=1)
    # Use replace instead of map for better pandas compatibility
    data['diagnosis'] = data['diagnosis'].replace({'M': 1, 'B': 0})
    return data

def add_sidebar():
    st.sidebar.header("Cell Nuclei Measurements")
    
    data = get_clean_data()
    
    slider_labels = [
        ("Radius (mean)", "radius_mean"),
        ("Texture (mean)", "texture_mean"),
        ("Perimeter (mean)", "perimeter_mean"),
        ("Area (mean)", "area_mean"),
        ("Smoothness (mean)", "smoothness_mean"),
        ("Compactness (mean)", "compactness_mean"),
        ("Concavity (mean)", "concavity_mean"),
        ("Concave points (mean)", "concave points_mean"),
        ("Symmetry (mean)", "symmetry_mean"),
        ("Fractal dimension (mean)", "fractal_dimension_mean"),
        ("Radius (se)", "radius_se"),
        ("Texture (se)", "texture_se"),
        ("Perimeter (se)", "perimeter_se"),
        ("Area (se)", "area_se"),
        ("Smoothness (se)", "smoothness_se"),
        ("Compactness (se)", "compactness_se"),
        ("Concavity (se)", "concavity_se"),
        ("Concave points (se)", "concave points_se"),
        ("Symmetry (se)", "symmetry_se"),
        ("Fractal dimension (se)", "fractal_dimension_se"),
        ("Radius (worst)", "radius_worst"),
        ("Texture (worst)", "texture_worst"),
        ("Perimeter (worst)", "perimeter_worst"),
        ("Area (worst)", "area_worst"),
        ("Smoothness (worst)", "smoothness_worst"),
        ("Compactness (worst)", "compactness_worst"),
        ("Concavity (worst)", "concavity_worst"),
        ("Concave points (worst)", "concave points_worst"),
        ("Symmetry (worst)", "symmetry_worst"),
        ("Fractal dimension (worst)", "fractal_dimension_worst"),
    ]
    input_dict = {}
    for label, key in slider_labels:
        input_dict[key] = st.sidebar.slider(
            label,
            min_value=float(data[key].min()),
            max_value=float(data[key].max()),
            value=float(data[key].mean())
        )
    return input_dict
       
    
def get_scaled_values(input_dict):
    data = get_clean_data()
    X = data.drop(['diagnosis'], axis=1)
    
    scaled_dict = {}
    
    for key, value in input_dict.items():
        max_val = X[key].max()
        min_val = X[key].min()
        scaled_value = (value - min_val) / (max_val - min_val)
        scaled_dict[key] = scaled_value
        
    return scaled_dict
    
   
def get_radar_chart(input_data):
    
    input_data = get_scaled_values(input_data)

    categories = ['Radius', 'Texture', 'Perimeter', "Area", 'Smoothness', 'Compactness', 
                  'Concavity', 'Concave Points', 'Symmetry', 'Fractional Dimension']

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[
            input_data['radius_mean'], input_data['texture_mean'], input_data['perimeter_mean'],
            input_data['area_mean'], input_data['smoothness_mean'], input_data['compactness_mean'],
            input_data['concavity_mean'], input_data['concave points_mean'], input_data['symmetry_mean'],
            input_data['fractal_dimension_mean']
        ],
        theta=categories,
        fill='toself',
        name='Mean Value'
    ))
    fig.add_trace(go.Scatterpolar(
        r=[
            input_data['radius_se'], input_data['texture_se'], input_data['perimeter_se'],
            input_data["area_se"], input_data["smoothness_se"], input_data['compactness_se'],
            input_data['concavity_se'], input_data['concave points_se'], input_data['symmetry_se'],
            input_data['fractal_dimension_se']
        ],
        theta=categories,
        fill='toself',
        name='Standard Error'
    ))
    fig.add_trace(go.Scatterpolar(
        r=[
            input_data['radius_worst'], input_data['texture_worst'], input_data['perimeter_worst'],
            input_data["area_worst"], input_data["smoothness_worst"], input_data['compactness_worst'],
            input_data['concavity_worst'], input_data['concave points_worst'], input_data['symmetry_worst'],
            input_data['fractal_dimension_worst']
        ],
        theta=categories,
        fill='toself',
        name='Worst Value'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True
    )
    return fig

def add_prediction(input_data):
    """
    Load model and scaler using joblib and make predictions.
    Includes error handling for missing model files.
    """
    try:
        # Use joblib for better ML model loading
        if not os.path.exists('model/model.pkl') or not os.path.exists('model/scaler.pkl'):
            st.error("❌ Model files not found. Please train the model first by running model/main.py")
            return
        
        model = joblib.load('model/model.pkl')
        scaler = joblib.load('model/scaler.pkl')
        
        input_array = np.array(list(input_data.values())).reshape(1, -1)
        input_array_scaled = scaler.transform(input_array)
        prediction = model.predict(input_array_scaled)
        
        st.subheader("Cell Cluster Prediction Result:")
        
        # Use Streamlit columns and proper styling instead of unsafe HTML
        col1, col2 = st.columns(2)
        
        with col1:
            if prediction[0] == 0:
                st.success("🟢 **Benign**")
            else:
                st.error("🔴 **Malicious**")
        
        # Get prediction probabilities
        probabilities = model.predict_proba(input_array_scaled)[0]
        
        with col2:
            st.metric("Benign Probability", f"{probabilities[0]:.2%}")
            st.metric("Malicious Probability", f"{probabilities[1]:.2%}")
        
        # Add disclaimer
        st.warning(
            "⚠️ **Important:** This app can assist medical professionals in making a diagnosis, "
            "but should NOT be used as a substitute for a professional medical diagnosis."
        )
        
    except Exception as e:
        st.error(f"❌ Error during prediction: {str(e)}")

def main():
    
    st.set_page_config(
        page_title="Breast Cancer Predictor",
        page_icon='👩‍⚕️',
        layout='wide',
        initial_sidebar_state='expanded'
    )
    
    # Load and apply custom CSS
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom CSS file not found. Using default styling.")

    input_data = add_sidebar()
    
    with st.container():
        st.title("🏥 Breast Cancer Predictor")
        st.write(
            "This application assists medical professionals in diagnosing breast cancer from tissue samples. "
            "It uses a machine learning model to predict whether a breast mass is benign or malignant based on "
            "cytology lab measurements. You can adjust the measurements using the sliders in the sidebar."
        )
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            radar_chart = get_radar_chart(input_data)
            st.plotly_chart(radar_chart, use_container_width=True)
        
        with col2:
            add_prediction(input_data)
   

if __name__ == '__main__':
    main()