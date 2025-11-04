
import json
import asyncio
from fastmcp import FastMCP
#  Komponenty LangChain  
from langchain_community.llms import LlamaCpp
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.documents import Document
#  Komponenty do bazy wektorowej (RAG) 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

#  Stałe 
SCIEZKA_DO_MODELU = "Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
NAZWA_PLIKU_JSON = "thecocktailsdb.json"
MODEL_EMBEDDINGOW = "all-MiniLM-L6-v2"
ADRES_SERWERA_LMSTUDIO = "http://localhost:1234/v1"

#  Funkcja 'create_document_from_drink' 
def create_document_from_drink(drink_data: dict) -> Document:
    nazwa = drink_data.get("name", "Brak nazwy")
    instrukcje = drink_data.get("instructions", "Brak instrukcji")
    
    skladniki_list = []
    for ing in drink_data.get("ingredients", []):
        name = ing.get("name")
        if not name:
            continue
        measure = ing.get("measure") 
        if measure:
            skladniki_list.append(f"{name.strip()} ({measure.strip()})")
        else:
            skladniki_list.append(name.strip())
            
    tekst_skladnikow = ", ".join(skladniki_list)
    page_content = f"Nazwa koktajlu: {nazwa}\nSkładniki: {tekst_skladnikow}\nInstrukcje: {instrukcje}"
    
    metadata = {
        "nazwa": nazwa,
        "kategoria": drink_data.get("category", "Brak"),
        "alkoholowy": drink_data.get("alcoholic", "Brak"),
        "tagi": drink_data.get("tags", [])
    }
    return Document(page_content=page_content, metadata=metadata)

#  Funkcja 'format_docs' 
def format_docs(docs: list[Document]) -> str:
    return "\n\n\n\n".join([d.page_content for d in docs])

print(f"Ładowanie modelu LlamaCpp z: {SCIEZKA_DO_MODELU}...")



print("Model LlamaCpp załadowany pomyślnie.")
# =================================================================
# GŁÓWNA LOGIKA APLIKACJI
# =================================================================

print("Uruchamianie aplikacji...")

#  Krok 1: Wczytanie i przetworzenie danych JSON 
print(f"Wczytywanie danych z {NAZWA_PLIKU_JSON}...")
try:
    with open(NAZWA_PLIKU_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    dokumenty_koktajli = [create_document_from_drink(drink) for drink in data]
    print(f"Załadowano {len(dokumenty_koktajli)} dokumentów koktajli.")

except FileNotFoundError:
    print(f"BŁĄD: Nie znaleziono pliku {NAZWA_PLIKU_JSON}!")
    exit()
except Exception as e:
    print(f"BŁĄD podczas wczytywania JSON: {e}")
    exit()


#  Krok 2: Inicjalizacja modelu embeddingów 
print(f"Ładowanie modelu embeddingów ({MODEL_EMBEDDINGOW})...")
embeddings = HuggingFaceEmbeddings(model_name=MODEL_EMBEDDINGOW)
print("Model embeddingów załadowany.")

#  Krok 3: Stworzenie bazy wektorowej FAISS  
print("Tworzenie bazy wektorowej FAISS...")
vector_store = FAISS.from_documents(dokumenty_koktajli, embeddings)
print("Baza wektorowa gotowa.")

#  Krok 4: Stworzenie Retrieversa 
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

#  Krok 5: Inicjalizacja LLM  
llm = LlamaCpp(
    model_path=SCIEZKA_DO_MODELU,
    n_gpu_layers=-1,  # Użyj GPU, jeśli jest dostępne (ustaw na 0 jeśli masz tylko CPU)
    n_batch=512,      # Wielkość przetwarzania wsadowego
    n_ctx=4096,       # Maksymalna długość kontekstu
    f16_kv=True,      # Musi być True dla Llama 3
    verbose=True,     # Pokazuj logi z LlamaCpp
)

#  Krok 6: Zdefiniowanie szablonu promptu RAG  
template = """
Jesteś ekspertem od koktajli. Odpowiedz na pytanie użytkownika bazując wyłącznie na poniższym kontekście. 
Jeśli w kontekście nie ma odpowiedzi, powiedz "Niestety, nie mam informacji na ten temat w mojej bazie koktajli.".
Nie wymyślaj składników ani instrukcji.

Kontekst (znalezione koktajle):

{context}

Pytanie użytkownika: {pytanie}

Odpowiedź:
"""
prompt = ChatPromptTemplate.from_template(template)

#  Krok 7: Zbudowanie pełnego łańcucha RAG 
rag_chain = (
    RunnableParallel(
        context=(retriever | format_docs),
        pytanie=RunnablePassthrough()
    )
    | prompt
    | llm
    | StrOutputParser()
)
print("Łańcuch RAG został pomyślnie zbudowany.")


#  Krok 8: Stworzenie serwera i NARZĘDZIA FastMCP 

print("Tworzenie serwera FastMCP...")
server = FastMCP(
    name="CocktailBotServer",
    stateless_http=True,
    instructions=(
        "Twoja rola to WYŁĄCZNIE kierowanie zapytań. NIE masz żadnej własnej wiedzy. "
        "Jesteś prostym botem, który przekazuje pytania do specjalistycznych systemów. "
        "NIGDY nie odpowiadaj na pytanie użytkownika bezpośrednio. "
        "Do WSZYSTKICH pytań użytkownika, bez względu na temat, MUSISZ użyć narzędzia 'ask_cocktail_bot'. "
        "Przekaż pytanie DOKŁADNIE tak, jak je otrzymałeś."
        
    )
)

@server.tool
async def ask_cocktail_bot(query: str) -> str: 
    """
    Odpowiada na pytania dotyczące koktajli używając lokalnej bazy RAG.
    
    Args:
        query: Pełne pytanie użytkownika.
        
    Returns:
        Odpowiedź tekstowa wygenerowana przez system RAG.
    """
    try:
        print(f"\n[NARZĘDZIE] Otrzymano zapytanie: {query}")
        

        response_text = await asyncio.to_thread(
            rag_chain.invoke,  
            query          
        )
        
        print(f"[NARZĘDZIE] Odpowiedź z RAG: {response_text}")
        return response_text
        
    except Exception as e:
        print(f"[NARZĘDZIE] BŁĄD: {e}")
        return f"Wystąpił błąd serwera: {e}"