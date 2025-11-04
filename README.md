# Projekt AI/ML: Asystent Koktajli (RAG + MCP)

Projekt ten jest implementacją narzędzia typu **RAG (Retrieval-Augmented Generation)** udostępnianego przez serwer **MCP (Model Context Protocol)**. 

Celem jest stworzenie inteligentnego asystenta, który potrafi odpowiadać na pytania dotyczące koktajli oraz sugerować drinki na podstawie podanych składników. Cała wiedza asystenta jest ograniczona *wyłącznie* do dostarczonego pliku `thecocktailsdb.json`, co oznacza, że nie będzie on odpowiadał na pytania spoza tej dziedziny.

---

## 🚀 Główne Funkcje

* **Odpowiadanie na pytania:** Możesz zapytać o przepis na dowolny koktajl z bazy (np. "Jak zrobić Mojito?").
* **Sugerowanie koktajli:** Możesz zapytać o koktajle zawierające konkretne składniki (np. "Co mogę zrobić z ginu i soku z cytryny?").
* **Ograniczona wiedza:** System jest "zmuszony" do korzystania wyłącznie z dostarczonych danych RAG i nie będzie odpowiadał na pytania ogólne (np. "Kto jest prezydentem Polski?").

---

## 🛠️ Użyte Technologie

* **Python 3.10+**
* **Serwer API:** `FastMCP` (zgodnie z wymaganiami)
* **Silnik RAG:** `LangChain`
* **Baza Wektorowa:** `FAISS` (do szybkiego przeszukiwania semantycznego)
* **Embeddingi:** `HuggingFaceEmbeddings` (model `all-MiniLM-L6-v2`)
* **Lokalny LLM:** `LlamaCpp` (do ładowania modeli GGUF bezpośrednio w Pythonie)
* **Klient:** `httpx` lub `LMStudio`(do komunikacji z serwerem z konsoli)

---

## ⚙️ Wymagania Wstępne

Przed instalacją upewnij się, że masz na swoim systemie:
1.  **Python 3.10** lub nowszy oraz `pip`.
2.  Pobrany plik modelu LLM w formacie **GGUF**. Projekt był testowany z modelem `Meta-Llama-3-8B-Instruct-Q4_K_M.gguf`.
    * *Możesz pobrać ten model (lub mniejszy, np. Q2_K) za pomocą aplikacji LM Studio.*
3.  Plik z danymi `thecocktailsdb.json` w głównym folderze projektu.

---

## 1. Instalacja

1.  Sklonuj repozytorium (lub pobierz pliki) i przejdź do folderu projektu.
2.  Stwórz i aktywuj środowisko wirtualne:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  Zainstaluj wszystkie wymagane biblioteki:
    ```bash
    pip install fastmcp langchain langchain_huggingface faiss-cpu llama-cpp-python httpx
    ```

---


## 2. Uruchomienie Narzędzia

Narzędzie składa się z dwóch części: serwera RAG i klienta konsolowego(lub LMStusio). Musisz je uruchomić w **dwóch osobnych terminalach**.

### Terminal 1: Uruchomienie Serwera RAG

W pierwszym terminalu (z aktywnym `.venv`) uruchom serwer `FastMCP`.

```bash
fastmcp run server.py:server --transport http --port 8000
```
W drugim terminalu (z aktywnym `.venv`) uruchom klienta

```bash
python client.py
```
---
KOD MOŻE ZAWIERAĆ BŁĘDY (nawet sporo :( )
Zadanie rozwiązywałem z pomocą gemini, gdyż nie miałem wystarczająco czasu na przeczytanie wystarczającej dokumentacji i napisanie całkowicie samemu kodu. Niemniej planuje nauczyć się w wolnym czasie wszystkiego, a zadanie chciałem wykonać by móc przejść do kolejnego etapu rekrutacji i nauczyć się wszystkiego po drodze. Jestem z kierunku SI na inżynierce, więc prędzej czy później i tak będę sie uczył podobnych rzeczy, a w tym momencie niestety brakuje mi czasu. Pozdrawiam :)
