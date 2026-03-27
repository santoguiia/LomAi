import reflex as rx
import ollama
from typing import List, Dict
from .personalities import PERSONALITIES, get_personality_prompt

# --- Configurações Visuais ---
BG_COLOR = "hsl(240, 10%, 4%)"
SIDEBAR_COLOR = "hsl(240, 10%, 8%)"
PRIMARY_COLOR = "hsl(262, 83%, 58%)"
TEXT_COLOR = "hsl(240, 5%, 90%)"
MESSAGES_BG = "hsl(240, 10%, 12%)"

class State(rx.State):
    """Estado da aplicação."""
    messages: List[Dict[str, str]] = []
    user_input: str = ""
    selected_model: str = "qwen2.5:3b"
    selected_personality: str = "Padrão"
    is_answering: bool = False
    
    # --- Setters Explícitos ---
    def set_input(self, val: str):
        self.user_input = val

    def change_model(self, val: str):
        self.selected_model = val

    def change_personality(self, val: str):
        self.selected_personality = val
        self.clear_chat() 

    def clear_chat(self):
        self.messages = []

    # --- Lógica do Chat ---
    def handle_key_down(self, key: str):
        if key == "Enter" and self.user_input:
            return State.handle_submit()

    @rx.event
    async def handle_submit(self):
        if not self.user_input.strip() or self.is_answering:
            return

        user_content = self.user_input
        self.messages.append({"role": "user", "content": user_content})
        self.user_input = ""
        self.is_answering = True
        self.messages.append({"role": "assistant", "content": ""})
        yield
        
        try:
            system_instruction = get_personality_prompt(self.selected_personality)
            full_history = [{"role": "system", "content": system_instruction}] + self.messages[:-1]
            
            stream = ollama.chat(
                model=self.selected_model,
                messages=full_history,
                stream=True,
            )
            
            response_text = ""
            for chunk in stream:
                content = chunk['message']['content']
                response_text += content
                self.messages[-1]["content"] = response_text
                yield 
                
        except Exception as e:
            self.messages[-1]["content"] = f"Erro Ollama: {str(e)}"
            yield
        finally:
            self.is_answering = False

# --- Componentes de UI ---

def Sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("LomAi", size="7", color=PRIMARY_COLOR, margin_bottom="1.5rem"),
            
            rx.button(
                rx.icon(tag="plus"),
                "Novo Chat",
                width="100%",
                variant="surface",
                on_click=State.clear_chat,
                cursor="pointer",
                margin_bottom="2rem"
            ),
            
            rx.spacer(),
            
            rx.vstack(
                rx.text("Personalidade", color="gray", size="2"),
                rx.select(
                    list(PERSONALITIES.keys()),
                    value=State.selected_personality,
                    on_change=State.change_personality,
                    width="100%",
                    variant="ghost",
                ),
                width="100%",
                padding_y="1rem"
            ),
            
            rx.vstack(
                rx.text("Modelo LLM", color="gray", size="2"),
                rx.select(
                    ["qwen2.5:3b", "qwen3-vl:2b", "llama3"],
                    value=State.selected_model,
                    on_change=State.change_model,
                    width="100%",
                    variant="ghost",
                ),
                width="100%",
                padding_top="0.5rem"
            ),
            
            padding="2rem",
            height="100vh",
            align_items="start",
        ),
        width="260px",
        background_color=SIDEBAR_COLOR,
        border_right="1px solid rgba(255,255,255,0.1)",
    )

def Message(msg: rx.Var) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(
                    tag=rx.cond(msg["role"] == "user", "user", "bot"),
                    size=20, 
                    color=rx.cond(msg["role"] == "user", "white", PRIMARY_COLOR)
                ),
                padding="8px",
                border_radius="8px",
                background_color=rx.cond(msg["role"] == "user", PRIMARY_COLOR, MESSAGES_BG),
                flex_shrink="0",
            ),
            rx.box(
                rx.markdown(msg["content"], color=TEXT_COLOR, font_size="15px"),
                padding_x="10px",
            ),
            align_items="start",
            spacing="3",
        ),
        width="100%",
        max_width="850px", # Aumentado de 750 para 850 para ganhar mais espaço horizontal
        padding_y="0.4rem", # Reduzido ainda mais para aproximar as conversas
        padding_x="1rem",
        border_radius="10px",
        background_color=rx.cond(msg["role"] == "user", "transparent", "rgba(255, 255, 255, 0.03)"),
    )

def ChatWindow() -> rx.Component:
    return rx.box(
        rx.scroll_area(
            rx.vstack(
                rx.foreach(State.messages, Message),
                padding_top="2rem",
                padding_bottom="12rem",
                width="100%",
                align_items="center",
                spacing="1", # Mínimo espaço vertical entre mensagens
            ),
            height="100vh",
            scrollbars="vertical",
        ),
        width="100%",
        background_color=BG_COLOR,
    )

def InputArea() -> rx.Component:
    return rx.box(
        rx.center(
            rx.hstack(
                rx.input(
                    placeholder="Envie uma mensagem...",
                    value=State.user_input,
                    on_change=State.set_input,
                    on_key_down=State.handle_key_down,
                    width="100%",
                    background_color=MESSAGES_BG,
                    border="none",
                    height="55px",
                    padding_x="1.5rem",
                    border_radius="20px",
                    color=TEXT_COLOR,
                    focus_style={"box-shadow": f"0 0 0 2px {PRIMARY_COLOR}"},
                ),
                rx.icon_button(
                    rx.icon(tag="send"),
                    on_click=State.handle_submit,
                    loading=State.is_answering,
                    background_color=PRIMARY_COLOR,
                    radius="full",
                    size="3",
                    cursor="pointer",
                    _hover={"transform": "scale(1.05)"},
                ),
                width="100%",
                max_width="850px", # Sincronizado com a largura das mensagens
                spacing="4",
            ),
            width="100%",
            height="140px",
            background=f"linear-gradient(to top, {BG_COLOR} 80%, transparent)",
            position="absolute",
            bottom="0",
            z_index="10",
        ),
        width="100%",
    )

def index() -> rx.Component:
    return rx.hstack(
        Sidebar(),
        rx.box(
            ChatWindow(),
            InputArea(),
            width="100%",
            height="100vh",
            position="relative",
        ),
        spacing="0",
        background_color=BG_COLOR,
    )

app = rx.App(
    theme=rx.theme(appearance="dark", has_background=True, accent_color="violet"),
)
app.add_page(index)
