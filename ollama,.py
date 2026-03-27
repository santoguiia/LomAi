import ollama
import sys

# ANSI Escape Codes for Colors
GREEN = "\033[92m"
RESET = "\033[0m"
CYAN = "\033[96m"

def chat():
    print(f"{CYAN}--- Conversa iniciada (digite 'sair' para encerrar) ---{RESET}")
    messages = []
    
    while True:
        try:
            # User input in green
            user_input = input(f"\n{GREEN}Você: ")
            print(RESET, end='') # Ensure text after input isn't green if it spills
            
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print(f"{CYAN}Encerrando chat...{RESET}")
                break
                
            messages.append({'role': 'user', 'content': user_input})
            
            print(f"{CYAN}IA: {RESET}", end='', flush=True)
            
            response_content = ""
            stream = ollama.chat(
                model='qwen2.5:3b',
                messages=messages,
                options={
                    'num_ctx': 2048,
                    'num_predict': 512,
                },
                stream=True,
            )

            for chunk in stream:
                content = chunk['message']['content']
                print(content, end='', flush=True)
                response_content += content
            
            print() # New line after response
            messages.append({'role': 'assistant', 'content': response_content})
            
        except KeyboardInterrupt:
            print(f"\n{CYAN}Encerrando chat...{RESET}")
            break
        except Exception as e:
            print(f"\nErro: {e}")
            break

if __name__ == "__main__":
    chat()