import streamlit as st
from mongodb_utils import connect_to_mongodb

users_collection = connect_to_mongodb("users")

# Function to get user info from the database
def get_user_info(username):
    return users_collection.find_one({"username": username})

# Function to update user info in the database
def update_user(username, Vocabulary, Sentence_Length, Sentence_Complexity, ranked_preferences, difficulty_level):
    users_collection.update_one(
        {"username": username},
        {
            "$set": {
                "Vocabulary": Vocabulary,
                "Sentence Length": Sentence_Length,
                "Sentence Complexity": Sentence_Complexity,
                "ranked_preferences": ranked_preferences,
                "difficulty_level": difficulty_level
            }
        }
    )
    

# Function to display the update user profile page
def update_profile_page():
    # Check if the user is logged in
    if "username" not in st.session_state:
        st.warning("Please log in first.")
        return
    else: 
        username = st.session_state.username
    user_info = get_user_info(username)

    # User Survey
    with st.form("register_form"):
        st.write("### 1. User Survey")
        question_preference = st.multiselect(
            "Selection of Preferred Question Types: Please list the following question types in order of your interest, starting with the most preferred.",
            ["Fill-in-the-Blank-with-Single-Word", "Fill-in-the-Blank-with-Phrase", "Sequence-Inference", "Main-Idea-Inference"]
        )

        ranked_preferences_container = st.container()

        st.write("### 2. Evaluation of Desired Problem-Solving Skills Improvement")
        st.write("Please indicate the extent to which you want to improve in the following areas using percentages. Ensure the total adds up to 100%.")
        Vocabulary = st.slider("Vocabulary", 0, 100, user_info["Vocabulary"])
        Sentence_Length = st.slider("Sentence Length", 0, 100, user_info["Sentence Length"])
        Sentence_Complexity = st.slider("Sentence Complexity", 0, 100, user_info["Sentence Complexity"])
        total_score = Vocabulary + Sentence_Length + Sentence_Complexity

        # Choose the difficulty level of starting problem solving
        st.write("### 3. Choose the difficulty level of starting problem solving")
        difficulty_level = st.selectbox(
            "Select your preferred difficulty level:",
            ("Level 1", "Level 2", "Level 3", "Level 4", "Level 5")
        )

        submit_button = st.form_submit_button("Update Profile")

        if submit_button:
            if len(question_preference) != 4:
                st.error("Please select your preferences before updating your profile.")
            elif total_score != 100:
                st.error("Total score must be 100 points. Please adjust it.")
            else:
                # Save updated user information to the database
                ranked_preferences = {}
                for i, pref in enumerate(question_preference):
                    ranked_preferences[pref] = i + 1
                ranked_preferences_list = [pref for pref, _ in sorted(ranked_preferences.items(), key=lambda x: x[1])]
                
                if total_score == 100:                
                    update_user(username, Vocabulary, Sentence_Length, Sentence_Complexity, ranked_preferences_list, difficulty_level)
                    st.success("Your profile has been successfully updated.")

                    with ranked_preferences_container:
                        st.write("#### Your ranked preferences")
                        for pref, rank in sorted(ranked_preferences.items(), key=lambda item: item[1]):
                            st.write(f"Rank {rank}: {pref}")

                else:
                    st.error("Total score must be 100 points. Please adjust it.")
