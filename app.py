import gradio as gr
import google.generativeai as genai
import os
import json
import pandas as pd
import tempfile
from dotenv import load_dotenv
import io

load_dotenv()
try:
    API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    print("Please set it or uncomment the .env loading if you're using a .env file.")
    exit()

genai.configure(api_key=API_KEY)

#LIMITATIONS IN FREE PLAN 30RPM 1000RPD
MODEL_NAME = "gemini-2.0-flash-lite"
model = genai.GenerativeModel(MODEL_NAME)
def extract_house_info(description: str) -> dict:
    prompt = f"""
    Extract the following information from the house description:
    - is_for_rent (boolean: true if for rent, false if for sale)
    - type (string: "apartment", "room", or "house". If not specified, default to "apartment")
    - bathrooms (integer: number of bathrooms, or null if not specified)
    - bedrooms (integer: number of rooms/bedrooms, or null if not specified)
    - price (float: numerical value of the price, or null if not specified indicate)
    - location (string : the location of the apartment or room or house, or null)
    - square_meters(integer : the square meters of the house, apartment, or room, null if not specified)

    The language of the description can be Greek or English.
    Provide the output in JSON format.

    Examples:

    Description: "Νοικιάζεται διαμέρισμα στο Κουκάκι δίπλα στον Φιλοπάππου , ανακαινισμένο, επιπλωμένο με όλες τις ηλεκτρικές συσκευές , 650 με ίντερνετ , μεσιτικό +6 €650 · Αθήνα, I Apartment - koukaki Message BbIIGdZv.com Apartment - koukaki €650"
    Output:
    ```json
    {{
      "is_for_rent": true,
      "type": "apartment",
      "bathrooms": null,
      "bedrooms": null,
      "price": 650.0,
      "location" : "Koukaki,Athens",
      "square_meters" : null
    }}
    ```

    Description: "Πωλείται κατοικία στον Τρίλοφο Θεσσαλονίκης, στο κέντρο του οικισμού, σε οικόπεδο 1.190 τ.μ. Η συνολική επιφάνεια του κτίσματος είναι 152 τ.μ. και αποτελείται από τρία επίπεδα: 1. Ισόγειο με ενιαία σαλοκουζίνα και, ελαφρώς υπερυψωμένα, 2 δωμάτια και μπάνιο. 2. Μεγάλη σοφίτα με μπαλκόνι. 3. Ημιυπόγειο χώρο με 2 δωμάτια και μικρή τουαλέτα-μπάνιο, ο οποίος έχει ξεχωριστή είσοδο, αλλά επικοινωνεί εσωτερικά και με το ισόγειο, με σκάλα. Όλα τα δωμάτια έχουν ανεξάρτητα μπαλκόνια. Διαθέτει 2 υπόγεια, ένα μεγάλο και ένα μικρότερο. Είναι χτισμένη σε ύψωμα και διαθέτει απεριόριστη θέα προς το Πλαγιάρι. Μέσο θέρμανσης καλοριφέρ με πετρέλαιο. Διαθέτει σύστημα βοηθητικής θέρμανσης από το τζάκι, το οποίο όταν φτάνει σε μια συγκεκριμένη θερμοκρασία κλείνει αυτόματα τον λέβητα του πετρελαίου και το νερό στα καλοριφέρ θερμαίνεται με το τζάκι. Υπάρχει δυνατότητα σύνδεσης με το φυσικό αέριο. Η κατοικία είναι συνδεδεμένη με την αποχέτευση. Περισσότερες πληροφορίες, φωτογραφίες, βίντεο κτλ. στο messenger. +30 €1 · Θέρμη, B 5 beds · 2 bath · Townhouse Message KLWA1hei.com 5 beds · 2 bath · Townhouse €"
    Output:
    ```json
    {{
      "is_for_rent": false,
      "type": "house",
      "bathrooms": 2,
      "rooms": 5,
      "price": 1.0,
      "location" : "Trilofo, Thessaloniki",
      "square_meters" : 152.0
    }}
    ```

    Description: "ΜΟΝΑΔΙΚΟ ΑΚΙΝΗΤΟ ΛΟΥΞ 45 τ.μ στην Πλάκα! Η ιστορική συνοικία της πλάκας βρίσκεται στην σκιά του Ιερού βράχου της Ακρόπολης και φιλοξενεί πλήθος μουσείων, θέατρα και χώρους όπου η τέχνη άνθησε στο χρόνο! Ένα μοναδικό ακίνητο στην μαγευτική πλάκα με ανεμπόδιστη θέα στην Ακρόπολη και όλη την Αθήνα! Βρίσκεται στον 4ο όροφο έχει 1 Υ/Δ  με μπαλκόνι, 1 κουζίνα , 1 μπάνιο, 1 σαλόνι με τζαμαρία και μπαλκόνι με ειδυλλιακή θέα! Υπάρχει αυτόνομη θέρμανση φυσικού αερίου, ηλιακός, τέντες, ελάχιστα κοινόχρηστα χωρίς ασανσέρ. Το ακίνητο είναι σε υπεράριστη κατάσταση με εξαιρετικές λεπτομέρειες του χώρου! Ένα ακίνητο για απαιτητικούς πελάτες με υψηλές προδιαγραφές! Μεσιτικό. +6 €285,000 · Αθήνα, I ΠΩΛΗΣΗ Message oJw58uk4.com ΠΩΛΗΣΗ €285,000"
    Output:
    ```json
    {{
      "is_for_rent": false,
      "type": "apartment",
      "bathrooms": 1,
      "rooms": 1,
      "price": 285000.0
      "location" : "Plaka, Athens",
      "square_meters" : 45.0
    }}
    ```

    Description: "APARTMENT FOR RENT - LEPTOKARIJA BEACH, PIERIA Just 80 meters from the sea, a fully furnished apartment for rent, ideal for summer holidays, in the popular resort Leptokarija, Pieria. Room layout: Dnevna soba …   See more · See original · Rate this translation +6 €65 · Λιτόχωρο, B 🏖️ IZDAJE SE APARTMAN – PLAŽA LEPTOKARIJE - 80 m OD MORA Message g9Essu2.com IZDAJE SE APARTMAN – PLAŽA LEPTOKARIJE - 80 m OD MORA €65"
    Output:
    ```json
    {{
      "is_for_rent": true,
      "type": "apartment",
      "bathrooms": null,
      "rooms": null,
      "price": 65.0,
      "location" : "Laptokarija, Pieria",
      "square_meters" : null
    }}
    ```

    Description: "Ενοικιάζεται μονοκατοικία δυορωφη 115 τμ στην αναβυσσο Αττική στη φεριζα έχει θέα προς την θάλασσα  ηλιακό θέρμανση τηλ 6979944375 +6 €650 · Καλύβια Θορικού, I Ενοικιαζεται Message RrSNk0M6Q.com Ενοικιαζεται €650"
    Output:
    ```json
    {{
      "is_for_rent": true,
      "type": "house",
      "bathrooms": null,
      "rooms": null,
      "price": 650.0,
      "location" : "Anavisos, Attiki",
      "square_meters" : 115.0
    }}
    ```

    You might find data that are not for houses, apartments, rooms. Do not include them inside the json
    examples :

    ```
    Example1 : "God bless. Starting from 100 Euros!!!! Your brother elias at your service . Repair. Sale. Installation.... Refrigerators. Washing machines. Dryers. Air conditioners. Ovens.... 6982225400 WhatsApp. Viber.... 6-month warranty after sale or repair.... This is from the grace of God. Thank you all +6 $100 · Αθήνα, I Trust 4all Message QgNQpaZr.com Trust 4all $100 "
    Example2 : "Παλαιοπωλείο αγοράζω παλιά έπιπλα μπουφέδες τραπεζαρίες σύνθετά βιτρίνες καναπέδες κρεβατοκάμαρες επίσης και μικροαντικείμενα γυαλικά σερβίτσια μπιμπλό ασημικά σκεύη ρολόγια κομπολόγια κοσμήματα παράσημα σπαθιά κι άλλα διάφορα του σπιτιού 694088501 FREE · Αθήνα, I Παλαιοπωλείο αγοράζω παλιά έπιπλα μπουφέδες τραπεζαρίες σύνθετά βιτρίνες καναπέδες κρεβατοκάμαρες επ Message jLyg5p2W.com Παλαιοπωλείο αγοράζω παλιά έπιπλα μπουφέδες τραπεζαρίες σύνθετά βιτρίνες καναπέδες κρεβατοκάμαρες επ FREE"
    Example3 : "Fix.buy.repair. 6982225400 Warranty after sale.fix +6 $100 · Αθήνα, I Elias Message HAFssENScv.com Elias $100"
    Example4 : "This content isn't available right now When this happens, it's usually because the owner only shared it with a small group of people, changed who can see it or it's been deleted."
    Example5 : "+6 uufW4.com Photos from person name post DiaAmTafnxN1jGsnI2YMO7uxLM9iNxXB95AEfpOTb76FOQyHt7T"
    ```

    Description: "{description}"
    Output:
    ```json
    """

    try:
        response = model.generate_content(prompt)
        # The model often wraps JSON in a markdown code block.
        # We need to extract the JSON string.
        text_response = response.text.strip()
        
        # Look for the start and end of the JSON block
        if text_response.startswith("```json"):
            json_str = text_response[len("```json"):].strip()
            if json_str.endswith("```"):
                json_str = json_str[:-len("```")].strip()
        else:
            json_str = text_response # Assume it's just the JSON if not wrapped

        # Attempt to parse the JSON
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw response text: {text_response}")
        return {"error": "JSON parsing failed", "raw_response": text_response}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": str(e)}


def process_csv_descriptions(filepath):
    """
    Reads descriptions from an uploaded CSV file, processes them using Gemini,
    and returns a DataFrame of extracted information and the filepath to a CSV file.
    """
    # Initialize output values for error cases
    empty_df = pd.DataFrame([{"Error": "No CSV file uploaded or processing failed."}])
    return_on_error = (empty_df, None) # Only two return values now

    if filepath is None:
        return return_on_error

    try:
        df = pd.read_csv(filepath)

        if df.empty:
            return pd.DataFrame([{"Error": "Uploaded CSV is empty or malformed."}]), None
        
        description_column_name = df.columns[0]
        descriptions_to_process = df[description_column_name].dropna().tolist()

        if not descriptions_to_process:
            return pd.DataFrame([{"Error": "No valid descriptions found in the CSV file."}]), None

        results_list = []
        for i, desc in enumerate(descriptions_to_process):
            if str(desc).strip() == description_column_name.strip():
                continue

            print(f"Processing description {i+1}/{len(descriptions_to_process)}: {str(desc)[:70]}...")

            extracted_data = extract_house_info(str(desc))
            
            # Prepare data for DataFrame
            row_data = {"Original Description": str(desc)[:200] + "..." if len(str(desc)) > 200 else str(desc)} # Truncate for display
            row_data.update(extracted_data) # Add extracted fields directly

            results_list.append(row_data)

        results_df = pd.DataFrame(results_list)

        # --- Save DataFrame to a temporary CSV file ---
        temp_csv_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        csv_filepath = temp_csv_file.name
        temp_csv_file.close() # Close the file handle to allow pandas to write to it
        results_df.to_csv(csv_filepath, index=False)
        print(f"Results saved to temporary CSV file: {csv_filepath}")

        # Return the DataFrame for display, and the filepath for CSV download
        return results_df, csv_filepath

    except pd.errors.EmptyDataError:
        return pd.DataFrame([{"Error": "The uploaded CSV file is empty."}]), None
    except pd.errors.ParserError as e:
        return pd.DataFrame([{"Error": f"Could not parse CSV. Please check format. Details: {e}"}]), None
    except Exception as e:
        print(f"An unexpected error occurred during processing: {e}")
        return pd.DataFrame([{"Error": f"An unexpected error occurred during processing: {e}"}]), None

# --- 5. Gradio Interface Definition ---
csv_input = gr.File(label="Upload CSV File (Single Column, First Row is Header/Link)", file_types=[".csv"], type="filepath")
output_dataframe = gr.DataFrame(label="Extracted House Information", interactive=False)
download_csv_button = gr.File(label="Download Extracted Data (CSV)", file_count="single", interactive=False) # Only CSV download button

# Create the Gradio interface
iface = gr.Interface(
    fn=process_csv_descriptions,
    inputs=csv_input,
    outputs=[output_dataframe, download_csv_button], # Only two outputs now
    title="House Description Extractor with Gemini 2.0 Flash-Lite",
    description=(
        "Upload a CSV file containing house descriptions (one description per row, first column only). "
        "The first row should be the header (e.g., the site link). "
        "The app will use Google Gemini 2.0 Flash-Lite to extract details like rent/sale status, type, bathrooms, rooms, and price. "
        "The extracted data will be displayed below and can be downloaded as a CSV file."
    ),
    allow_flagging="never",
    theme=gr.themes.Soft(),
    # examples=[
    #     # Add a placeholder example CSV path here if you have one locally for quick testing
    #     # 'path/to/your/example.csv'
    # ]
)

# Launch the Gradio app
if __name__ == "__main__":
    print("Starting Gradio app...")
    print("Ensure GOOGLE_API_KEY environment variable is set.")
    iface.launch(share=True) # Set share=True for a public link (for testing/sharing)
                            # Set share=False for local-only access