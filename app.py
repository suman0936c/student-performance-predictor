import streamlit as st
import pandas as pd
import joblib

# --- 1. SET UP PAGE ---
st.set_page_config(page_title="Student Score Predictor", page_icon="🎓", layout="wide")

# --- 2. LOAD THE MODEL AND PREPROCESSOR ---
try:
    model = joblib.load('student_performance_model.joblib')
    preprocessor = joblib.load('student_data_preprocessor.joblib')
except FileNotFoundError:
    st.error("Model or preprocessor files not found. Make sure 'student_performance_model.joblib' and 'student_data_preprocessor.joblib' are in the same directory as app.py.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred loading the files: {e}")
    st.stop()

# --- 3. SET UP THE USER INTERFACE (UI) ---
st.title('🎓 Student Performance Predictor & Advisor')
st.write("Enter the student's details below to predict their final exam score and get personalized feedback.")
st.markdown("---")

# Use columns for a cleaner layout
col1, col2, col3 = st.columns(3)

# --- Column 1: Academic Info ---
with col1:
    st.subheader("Academic Info")
    previous_scores = st.number_input('Previous Exam Score (0-100)', min_value=0, max_value=100, value=75)
    hours_studied = st.slider('Hours Studied (per week)', min_value=1, max_value=45, value=20)
    attendance = st.slider('Attendance (%)', min_value=60, max_value=100, value=90)
    tutoring_sessions = st.slider('Tutoring Sessions (per week)', min_value=0, max_value=8, value=1)
    learning_disabilities = st.selectbox('Learning Disabilities', ['No', 'Yes'])
    extracurricular = st.selectbox('Extracurricular Activities', ['Yes', 'No'])

# --- Column 2: Home Environment ---
with col2:
    st.subheader("Home Environment")
    # !! UPDATE THESE OPTIONS to match your data !!
    parental_involvement = st.selectbox('Parental Involvement', ['High', 'Medium', 'Low'])
    parental_education = st.selectbox('Parental Education Level', ["Bachelor's", "Master's", "High School", "Some College", "PhD", "None"])
    family_income = st.selectbox('Family Income', ['High', 'Medium', 'Low'])
    internet_access = st.selectbox('Internet Access', ['Yes', 'No'])
    access_to_resources = st.selectbox('Access to Resources', ['Good', 'Average', 'Poor'])
    distance_from_home = st.selectbox('Distance from Home', ['Short', 'Medium', 'Long'])

# --- Column 3: Personal & School ---
with col3:
    st.subheader("Personal & School")
    sleep_hours = st.slider('Sleep Hours (per night)', min_value=4.0, max_value=10.0, value=7.0, step=0.5)
    physical_activity = st.slider('Physical Activity (days/week)', min_value=0, max_value=7, value=3)
    gender = st.selectbox('Gender', ['Female', 'Male']) # Add 'Other' if in your data
    motivation_level = st.selectbox('Motivation Level', ['High', 'Medium', 'Low'])
    teacher_quality = st.selectbox('Teacher Quality', ['Good', 'Average', 'Poor'])
    school_type = st.selectbox('School Type', ['Public', 'Private'])
    peer_influence = st.selectbox('Peer Influence', ['Positive', 'Negative', 'Neutral'])


# --- 4. CREATE THE PREDICTION BUTTON ---
st.markdown("---")
if st.button('🚀 Predict Score & Get Advice', use_container_width=True):
    
    # --- 5. COLLECT ALL 19 INPUTS INTO A DATAFRAME ---
    try:
        input_data = pd.DataFrame({
            'Hours_Studied': [hours_studied],
            'Attendance': [attendance],
            'Parental_Involvement': [parental_involvement],
            'Access_to_Resources': [access_to_resources],
            'Extracurricular_Activities': [extracurricular],
            'Sleep_Hours': [sleep_hours],
            'Previous_Scores': [previous_scores],
            'Motivation_Level': [motivation_level],
            'Internet_Access': [internet_access],
            'Tutoring_Sessions': [tutoring_sessions],
            'Family_Income': [family_income],
            'Teacher_Quality': [teacher_quality],
            'School_Type': [school_type],
            'Peer_Influence': [peer_influence],
            'Physical_Activity': [physical_activity],
            'Learning_Disabilities': [learning_disabilities],
            'Parental_Education_Level': [parental_education],
            'Distance_from_Home': [distance_from_home],
            'Gender': [gender]
        }, index=[0])

        # --- 6. PROCESS THE DATA AND PREDICT ---
        processed_input = preprocessor.transform(input_data)
        prediction = model.predict(processed_input)
        
        # --- 7. SAVE TO SESSION STATE ---
        st.session_state['prediction'] = prediction[0]
        # We also save the inputs to use for feedback
        st.session_state['inputs'] = input_data.to_dict('records')[0]
        
    except Exception as e:
        st.error(f"An error occurred during prediction: {e}")
        st.error("Please ensure all selectbox options exactly match the original data.")

# --- 8. DISPLAY THE SAVED PREDICTION & FEEDBACK ---
if 'prediction' in st.session_state:
    
    prediction_value = st.session_state['prediction']
    inputs = st.session_state['inputs']
    
    # Create a container for the result
    st.markdown("---")
    st.subheader("Predicted Score:")
    st.metric(label="Predicted Exam Score", value=f"{prediction_value:.2f}")

    # --- 9. NEW (v2): PERSONALIZED FEEDBACK LOGIC ---
    st.subheader("Personalized Feedback:")
    feedback_list = []
    
    # --- NEW: Logic for IMPROVEMENT ---
    # We add +2 to create a "buffer", so it only triggers for real improvements
    if prediction_value > inputs['Previous_Scores'] + 2:
        feedback_list.append(f"🎉 **Great Improvement!** Your 'Previous Score' was {inputs['Previous_Scores']}, but your predicted score is {prediction_value:.2f}. This shows your current habits are very effective. Keep it up!")

    # --- NEW: Logic for a SCORE DROP ---
    # We add -2 as a buffer
    elif prediction_value < inputs['Previous_Scores'] - 2:
        feedback_list.append(f"💡 **Insight:** Your 'Previous Score' was {inputs['Previous_Scores']}, but your predicted score is {prediction_value:.2f}. The model sees that other factors might be pulling your score down. See the action items below.")
    
    # --- Logic for stable scores ---
    else:
         feedback_list.append(f"👍 **Stable Performance:** Your predicted score of {prediction_value:.2f} is very close to your previous score of {inputs['Previous_Scores']}. This shows you are consistent. See below for tips to break through to the next level.")


    # --- Logic for controllable features (always shows) ---
    
    # Hours Studied
    if inputs['Hours_Studied'] < 40:
        feedback_list.append(f"📈 **Top Priority:** Your 'Hours Studied' is {inputs['Hours_Studied']}. The model shows that students with top scores often study 40+ hours. This is likely the biggest lever you can pull to increase your score.")
    elif inputs['Hours_Studied'] >= 40:
         feedback_list.append(f"👍 **Great Work:** You are studying {inputs['Hours_Studied']} hours per week. This is a key habit for high scores.")

    # Attendance
    if inputs['Attendance'] < 95:
        feedback_list.append(f"➡️ **Action Item:** Your 'Attendance' is {inputs['Attendance']}%. Increasing this to 95-100% is a simple but powerful way to improve your score.")

    # Sleep
    if inputs['Sleep_Hours'] < 8:
        feedback_list.append(f"➡️ **Action Item:** You're getting {inputs['Sleep_Hours']} hours of sleep. The model may have learned that performance peaks for students who get 8-9 hours. Try going to bed 30 minutes earlier.")
    
    # Tutoring
    if inputs['Tutoring_Sessions'] < 3:
        feedback_list.append(f"💡 **Suggestion:** You have {inputs['Tutoring_Sessions']} tutoring sessions. If you are struggling, increasing this could provide a significant boost.")
        
    # Extracurriculars
    if inputs['Extracurricular_Activities'] == 'Yes':
         feedback_list.append(f"💡 **Insight:** 'Extracurricular Activities' are great, but they take time. The model may have learned this correlates with a slight score drop. Be sure to balance your time and study hours effectively.")

    # Display the feedback
    for feedback_item in feedback_list:
        st.info(feedback_item)