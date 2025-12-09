import os
import spacy
import requests
import asyncio
import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Setup Google Gemini
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)

# --- STEP 1: EXTRACTION (spaCy + Gemini Fallback) ---
def extract_entities(text: str):
    """
    Extracts Molecule and Disease using spaCy + LLM Cleanup.
    """
    doc = nlp(text)
    
    # Use Gemini with modern LangChain API
    extraction_prompt = PromptTemplate(
        input_variables=["text"],
        template="Extract the 'Molecule' and 'Disease' from this text: '{text}'. Return ONLY JSON format like: {{\"molecule\": \"name\", \"disease\": \"name\"}}. If not found, return null."
    )
    
    # Modern LangChain: Use pipe operator or invoke
    chain = extraction_prompt | llm
    result = chain.invoke({"text": text})
    
    # Extract content from AIMessage
    result_text = result.content if hasattr(result, 'content') else str(result)
    
    # Clean up response if the AI adds "```json" markdown
    result_text = result_text.replace("```json", "").replace("```", "").strip()
    return result_text

# --- STEP 2: WORKER AGENTS ---

async def get_clinical_trials(molecule: str, disease: str):
    """Worker 1: Hits ClinicalTrials.gov API"""
    if not molecule or molecule == "null": 
        return "No specific trials found (missing molecule name)."
    
    query = f"{molecule} {disease}".replace("null", "").strip()
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {"query.term": query, "filter.overallStatus": "RECRUITING", "pageSize": 3}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            studies = data.get('studies', [])
            if not studies: 
                return f"No active trials found for {query}."
            
            study_list = []
            for s in studies:
                title = s['protocolSection']['identificationModule'].get('officialTitle', 'No Title')
                study_list.append(f"- {title}")
            return "\n".join(study_list)
    except Exception as e:
        return f"Error fetching trials: {e}"
    return "No trials found."

async def get_market_data_raw(molecule: str):
    """
    Fetch market-related raw data from FDA APIs.
    Returns a dict WITHOUT interpretation.
    """
    results = {}

    # Manufacturer count
    try:
        ndc_url = "https://api.fda.gov/drug/ndc.json"
        params = {"search": f"active_ingredient:{molecule}", "limit": 100}
        r = requests.get(ndc_url, params=params, timeout=10).json()
        results["manufacturers"] = len({item.get("labeler_name", "") for item in r.get("results", [])})
    except:
        results["manufacturers"] = "N/A"

    # FDA approvals
    try:
        fda_url = "https://api.fda.gov/drug/drugsfda.json"
        params = {"search": f"products.active_ingredients.name:{molecule}", "limit": 50}
        r = requests.get(fda_url, params=params, timeout=10).json()
        results["approvals"] = len(r.get("results", []))
    except:
        results["approvals"] = "N/A"

    # Adverse events
    try:
        event_url = "https://api.fda.gov/drug/event.json"
        params = {"search": f"patient.drug.medicinalproduct:{molecule}", "count": "patient.drug.medicinalproduct.exact"}
        r = requests.get(event_url, params=params, timeout=10).json()
        results["safety_reports"] = sum([row.get("count", 0) for row in r.get("results", [])])
    except:
        results["safety_reports"] = "N/A"

    return results


async def get_disease_info_raw(disease: str):
    """
    Fetch disease-related raw data from PubMed + OpenTargets.
    Returns a dict WITHOUT interpretation.
    """
    results = {}

    # PubMed publication count
    try:
        pubmed_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {"db": "pubmed", "term": disease, "retmode": "json"}
        r = requests.get(pubmed_url, params=params, timeout=10).json()
        results["publications"] = r.get("esearchresult", {}).get("count", "N/A")
    except:
        results["publications"] = "N/A"

    # OpenTargets gene associations
    try:
        ot_url = "https://api.opentargets.io/v3/platform/public/search"
        r = requests.get(ot_url, params={"q": disease, "size": 5}, timeout=10).json()
        results["related_genes"] = [hit.get("id") for hit in r.get("data", [])]
    except:
        results["related_genes"] = []

    return results



# --- STEP 3: ORCHESTRATOR ---

class UserQuery(BaseModel):
    prompt: str

@app.post("/generate_report")
async def generate_report(query: UserQuery):
    print(f"Received query: {query.prompt}")
    
    # 1. Extract Molecule and Disease
    extraction_json = extract_entities(query.prompt)
    print(f"Extracted entities: {extraction_json}")
    
    try:
        entities = json.loads(extraction_json)
    except:
        entities = {"molecule": "Unknown", "disease": "Unknown"}
    
    molecule = entities.get("molecule")
    disease = entities.get("disease")

    # 2. Parallel API calls (clinical trials + raw data)
    task_trials = get_clinical_trials(molecule, disease)
    task_market_raw = get_market_data_raw(molecule)
    task_disease_raw = get_disease_info_raw(disease)

    trials_data, market_raw, disease_raw = await asyncio.gather(
        task_trials, task_market_raw, task_disease_raw
    )

    # 3. Generate dynamic interpretations using LLM
    market_prompt = f"""
    You are a pharmaceutical market analyst.
    Here is the market data for {molecule}:

    - Manufacturers: {market_raw['manufacturers']}
    - FDA Approvals: {market_raw['approvals']}
    - Adverse Events: {market_raw['safety_reports']}

    Write a professional market insight in Markdown. Focus on market size, competition, and usage trends.
    """
    disease_prompt = f"""
    You are a medical research analyst.
    Here is the disease data for {disease}:

    - PubMed publications: {disease_raw['publications']}
    - Key associated genes: {', '.join(disease_raw['related_genes']) or 'N/A'}

    Write a professional disease overview in Markdown. Include research intensity, biological insights, and unmet needs.
    """

    market_data = llm.invoke(market_prompt).content
    disease_data = llm.invoke(disease_prompt).content


    # 4. Final report generation
    report_prompt = PromptTemplate(
        input_variables=["molecule", "disease", "trials", "market", "disease_info"],
        template="""
        You are a Senior Pharmaceutical Strategy Consultant.
        Generate a professional Innovation Report.
        
        SUBJECT: {molecule} for {disease}
        
        DATA COLLECTED:
        1. Clinical Trials Status:
        {trials}
        
        2. Market Analysis:
        {market}
        
        3. Disease Context:
        {disease_info}
        
        OUTPUT FORMAT:
        Use Markdown.
        - Executive Summary
        - Clinical Landscape (Bulleted list)
        - Commercial Opportunity
        - Recommendation (Go/No-Go)
        """
    )

    final_chain = report_prompt | llm
    final_result = final_chain.invoke({
        "molecule": molecule if molecule else "Target Molecule",
        "disease": disease if disease else "Target Disease",
        "trials": trials_data,
        "market": market_data,
        "disease_info": disease_data
    })

    final_report = final_result.content if hasattr(final_result, 'content') else str(final_result)

    return {"report": final_report, "extracted": entities}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)