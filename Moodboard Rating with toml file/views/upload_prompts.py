import streamlit as st
import psycopg2
import pandas as pd

# Database connection configuration
db_connection = {
    "host": "34.93.64.44",
    "port": "5432",
    "dbname": "genai",
    "user": "postgres",
    "password": "postgres-genai"
}

# Function to fetch data from the PostgreSQL database
def fetch_data_from_db():
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_connection)
        query = "SELECT * FROM prompts;"  # SQL query to fetch all data from 'upload_prompts' table
        df = pd.read_sql(query, conn)  # Using pandas to fetch data into a dataframe
        conn.close()  # Close the connection
        return df
    except psycopg2.OperationalError as e:
        st.error(f"OperationalError: Unable to connect to the database: {e}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Function to check for duplicate prompts in the database
def check_duplicate_prompt(image_prompt):
    try:
        conn = psycopg2.connect(**db_connection)
        cursor = conn.cursor()
        query = "SELECT 1 FROM prompts WHERE image_prompts = %s LIMIT 1;"  # Check if prompt exists
        cursor.execute(query, (image_prompt,))
        result = cursor.fetchone()
        conn.close()  # Close the connection
        return result is not None  # If prompt exists, return True
    except Exception as e:
        st.error(f"Error checking for duplicate prompt: {e}")
        return False

# Function to insert a new prompt into the PostgreSQL database
def insert_new_prompt(serial_no, image_prompt):
    try:
        conn = psycopg2.connect(**db_connection)
        cursor = conn.cursor()
        query = """
        INSERT INTO prompts (sno, image_prompts)
        VALUES (%s, %s);
        """
        cursor.execute(query, (serial_no, image_prompt))
        conn.commit()  # Commit the transaction
        conn.close()  # Close the connection
        st.success("New prompt added successfully!")
    except Exception as e:
        st.error(f"Error inserting new prompt: {e}")

# Streamlit app layout
st.title("Upload Prompts")

# Section to Add New Prompt
st.subheader("Add New Prompt")

# Streamlit form for adding a new prompt
with st.form(key="new_prompt_form"):
    serial_no = st.text_input("Serial No.")
    image_prompt = st.text_area("Image Prompt")
    submit_button = st.form_submit_button("Add Prompt")

    # If the form is submitted, insert new data into the database
    if submit_button:
        if serial_no.isdigit():  # Check if serial_no is a valid integer
            # Check if the prompt already exists
            if check_duplicate_prompt(image_prompt):
                st.warning("This prompt already exists. Please enter a unique prompt.")
            else:
                # Insert the new prompt if it's unique
                insert_new_prompt(serial_no, image_prompt)
                # Re-fetch the data after insertion
                st.success("Prompt added successfully. Refreshing data...")
                df = fetch_data_from_db()

# Fetch the data from the database
df = fetch_data_from_db()

# Check if the DataFrame is not None and not empty
if df is not None and not df.empty:
    # Sort the DataFrame by 'sno'
    df = df.sort_values(by="sno", ascending=True)

    st.write("Data from the 'upload_prompts' table (sorted by 'sno'):")
    # Display the data as an interactive table
    st.dataframe(df, hide_index=True)
else:
    st.write("No data available.")
