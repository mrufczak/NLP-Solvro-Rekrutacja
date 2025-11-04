import asyncio
import httpx
import random
import json 

SERVER_URL = "http://localhost:8000/mcp"

HEADERS = {
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json"
}

async def main():
    print(f"Łączenie z serwerem koktajli (w trybie stateless) pod adresem: {SERVER_URL}")
    print("Wpisz swoje pytanie lub 'exit' aby zakończyć.")
    
    async with httpx.AsyncClient() as client:
        while True:
            query = input("\nTy: ")
            if query.lower() == 'exit':
                break
            
            print("Bot myśli...")
            
            payload = {
                "jsonrpc": "2.0",
                "id": random.randint(1, 100000),
                "method": "tools/call",
                "params": {
                    "name": "ask_cocktail_bot",
                    "arguments": {
                        "query": query
                    }
                }
            }
            
            try:
                async with client.stream("POST", SERVER_URL, json=payload, headers=HEADERS, timeout=300.0) as response:
                    
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        
                        if line.startswith("data:"):

                            json_data_string = line.removeprefix("data:").strip()
                            
                            response_data = json.loads(json_data_string)
  
                            answer = response_data.get("result", {}).get("content", [{}])[0].get("text", "Brak odpowiedzi tekstowej.")
                            
                            print(f"Cocktail Bot: {answer}")

                            break
                            
                        elif line.startswith(": ping"):
    
                            print("...")
                            pass
            except httpx.HTTPStatusError as e:
                print(f"\nBŁĄD: Serwer zwrócił błąd HTTP {e.response.status_code}")
                print(f"Treść błędu: {e.response.text}")
            except httpx.RequestError as e:
                print(f"\nBŁĄD: Nie można połączyć się z serwerem.")
                print(f"Szczegóły błędu: {e}")
            except Exception as e:
                print(f"\nWystąpił nieoczekiwany błąd: {e}")

if __name__ == "__main__":
    asyncio.run(main())