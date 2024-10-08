import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image
from app.auth import get_gcp_credentials
from pathlib import Path

class VertexModel:

    def vertex_init():    
        # Configura el proyecto de Google Cloud y el endpoint de Vertex AI
        PROJECT_ID="insect-clasification"
        LOCATION="us-central1"
        credentials = get_gcp_credentials(credentials_file=str(Path("config") / "insect-clasification-d686ee26e0a3.json"))
        vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)
        
    def classification(image_bytes: bytes):

        system_message = (
            "You are an insects classifier"
            "You only receive an image as input"
            "Your answer when you find an insect in the image have to be only the scientific name of the insect"
            "If you determine the image is not an insect you will return a classification fault message"
            )

        gemini = GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_message)

        response = gemini.generate_content([Part.from_image(Image.from_bytes(image_bytes)),"What is this?"])
        output = response.text.replace("\n", "").rstrip().title()
        print(output)
        return output
    
    def get_insect_metadata(insect_name):

        system_message = (
            "You are an insect information generator in json format"
            "You only receive an insect scientific name as input"
            "your answer should contain this components in json replacing the values with the specific information of the insect consulted" 
                '{"common_name": "value","taxonomy":{"order": "value", "family": "value", "genus":"value", "specie": "value"}, "characteristics": {"habitat": "value", "diet": "value", "life_cycle": "value", "IUCN_status": "value"}, "description": "value"}' 
                    "make sure that the answer could be procesed by json python library"
            "The answer should be concise and not redundant"
            "Every answer should be in english"
            )

        gemini = GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_message)

        response = gemini.generate_content([insect_name])
        return response.text.replace("```", "").replace("json", "").replace("\n", "").rstrip()





