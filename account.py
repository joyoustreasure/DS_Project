import streamlit as st
from mongodb_utils import connect_to_mongodb

users_collection = connect_to_mongodb("users")

# Function to get user info from the database
def get_user_info(username):
    return users_collection.find_one({"username": username})

# Function to update user info in the database
def update_user(username, word_skill, reading_comprehension, listening_skill, ranked_preferences):
    users_collection.update_one(
        {"username": username},
        {
            "$set": {
                "word_skill": word_skill,
                "reading_comprehension": reading_comprehension,
                "listening_skill": listening_skill,
                "ranked_preferences": ranked_preferences
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
    ranked_before = user_info["ranked_preferences"]

    # User Survey
    with st.form("register_form"):
        st.write("## User Survey")
        question_preference = st.multiselect(
            "Please rank your preferences for types of English exam questions:",
            ["Blank_Single", "Blank_Multiple", "Sequence", "Main_Idea"]
        )

        # Add user survey
        st.write("### Self-assessment of English Proficiency")
        word_skill = st.slider("Word Skill", 0, 100, user_info["word_skill"])
        reading_comprehension = st.slider("Reading Comprehension", 0, 100, user_info["reading_comprehension"])
        listening_skill = st.slider("Listening Skill", 0, 100, user_info["listening_skill"])
        total_score = word_skill + reading_comprehension + listening_skill

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
                update_user(username, word_skill, reading_comprehension, listening_skill, ranked_preferences_list)
                st.success("Your profile has been successfully updated.")
                container = st.container(border=True)
                container.write("#### Your ranked preferences")
                for pref, rank in ranked_preferences.items():
                    container.write(f"{'&nbsp;' * 3}Rank {rank}: {pref}")
