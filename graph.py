import os
from typing import TypedDict, List

from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from google import genai
from langchain_tavily import TavilySearch


class NGOState(TypedDict):
    name: str
    search_results: List[dict]
    extracted: dict

llm = genai.Client()
tavily = TavilySearch(max_results=5)

def search_web(state: NGOState) -> NGOState:
    # Use Tavily to search info about the NGO
    org = state["name"]
    results = tavily.invoke({"query": f"{org} nonprofit organization overview"})
    state["search_results"] = results
    return state

def extract_info(state: NGOState) -> NGOState:
    # Use Gemini to turn raw results into JSON
    org = state["name"]
    results = state["search_results"]

    # LLM prompt: ask for JSON
    system = (
        "You are a data extraction assistant. "
        "Given web search results about a nonprofit organization, "
        "produce a single JSON object with fields: "
        "Your Name, Organization Name, Type of organization, Website URL, Contact name, Email of contact, Area of activity, Revenue, Number of employees, Countries served or impacted by the services of the organization (not necessarily where the org is located), Done? (Y/N), Comments. "

        "IMPORTANT FORMAT RULES:\n"
        "- 'Type of organization' MUST be 1–3 words only (e.g., 'International NGO', 'Medical charity', 'Nonprofit').\n"
        "- If 'Contact name' is not explicitly found, write exactly 'N/A'.\n"
        "- If 'Email of contact' is not explicitly found, write exactly 'N/A'.\n"
        "- 'Area of activity' MUST be 1–3 words only (e.g., 'Humanitarian aid', 'Healthcare', 'Disaster relief').\n"
        "- If 'Revenue' is not explicitly found, write exactly 'N/A'.\n"
        "- If 'Number of employees' is not explicitly found, write exactly 'N/A'.\n"
        "- 'Comments' MUST be a short neutral blurb (1–2 sentences, max 40 words) summarizing the organization’s mission and activities.\n"

        "- Do NOT use full sentences.\n"
        "- Do NOT guess or invent contact details.\n"

        "Return ONLY valid JSON, no explanation."
    )

    user = f"""
Organization: {org}

Search results:
{results}

Return ONLY valid JSON with this schema:
{{
    "Your Name": "...",
    "Organization Name": "...",
    "Type of organization": "...",
    "Website URL": "...",
    "Contact name": "...",
    "Email of contact": "...",
    "Area of activity": "...",
    "Revenue": "...",
    "Number of employees": "...",
    "Countries served or impacted by the services of the organization (not necessarily where the org is located)": "...",
    "Done? (Y/N)": "...",
    "Comments": "..."
}}
"""

    prompt = system + "\n\n" + user

    # Call Gemini
    response = llm.models.generate_content(
        model="gemini-2.0-flash",  # or "gemini-1.5-pro", etc.
        contents=prompt,
    )

    text = response.text

    # --- Parse JSON with fallback ---
    import json
    import re

    try:
        data = json.loads(text)
    except Exception:
        # fallback if model returns extra text
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            try:
                data = json.loads(match.group(0))
            except Exception:
                data = None
        else:
            data = None

    if not data:
        # Fallback so pipeline never crashes
        data = {
            "Your Name": "CP",
            "Organization Name": org,
            "Type of organization": "",
            "Website URL": "",
            "Contact name": "",
            "Email of contact": "",
            "Area of activity": "",
            "Revenue": "",
            "Number of employees": "",
            "Countries served or impacted by the services of the organization (not necessarily where the org is located)": "",
            "Done? (Y/N)": "Y",
            "Comments": "",
        }

    state["extracted"] = data
    return state

def build_graph():
    graph = StateGraph(NGOState)

    graph.add_node("search_web", search_web)
    graph.add_node("extract_info", extract_info)

    graph.set_entry_point("search_web")
    graph.add_edge("search_web", "extract_info")
    graph.add_edge("extract_info", END)

    return graph.compile()

if __name__ == "__main__":
    # simple test
    app = build_graph()
    result = app.invoke({"name": "Doctors Without Borders"})
    print(result["extracted"])
