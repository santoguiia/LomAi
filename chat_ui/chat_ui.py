import reflex as rx
import ollama
import re
import time
import random
import asyncio
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
    messages: List[Dict[str, str]] = [
        {
            "role": "assistant",
            "content": "[LOMAI]: Bom dia, vida! Dormiu bem? Acordou tão cedo hoje...\n[CENA]: *Olha pra você sorrindo docemente enquanto se espreguiça de pijama.*",
            "ui_content": "☀️ Bom dia, vida! Dormiu bem? Acordou tão cedo hoje...\n\n*Ela olha pra você sorrindo docemente enquanto se espreguiça de pijama.*",
            "time": "08:00"
        }
    ]
    user_input: str = ""
    selected_model: str = "qwen2.5:3b"
    selected_personality: str = "Padrão"
    is_answering: bool = False
    
    # --- Status do RPG ---
    rpg_love: str = "50"
    rpg_hunger: str = "80"
    rpg_energy: str = "100"
    rpg_money: str = "100,00"
    rpg_local: str = "Casa"
    rpg_horario: str = "08:00"
    rpg_dia: int = 1
    is_working: bool = False # Flag para alternar os botões de ação
    
    # Time-Stamping System (Tempo real)
    last_interaction_time: float = 0.0
    last_tick_time: float = 0.0
    clock_started: bool = False
    
    # Variáveis de cálculo fracionário (Decaimento ao longo do tempo)
    love_debt: float = 0.0
    hunger_debt: float = 0.0
    
    # Sistema de Carreira V4.0
    rpg_xp: int = 0
    rpg_job: str = "Desempregado"
    consecutivos_erros: int = 0
    trabalhou_hoje: bool = False
    horas_trabalhadas_hoje: int = 0
    
    # --- Mini-Jogo de Trabalho ---
    current_puzzle_text: str = ""
    current_puzzle_answer: str = ""

    # --- Setters Explícitos ---
    def set_input(self, val: str):
        self.user_input = val

    def change_model(self, val: str):
        self.selected_model = val

    def change_personality(self, val: str):
        self.selected_personality = val
        self.clear_chat() 

    def clear_chat(self):
        # Reset RPG Stats
        self.rpg_love = "50"
        self.rpg_hunger = "80"
        self.rpg_energy = "100"
        self.rpg_money = "100,00"
        self.rpg_local = "Casa"
        self.rpg_horario = "08:00"
        
        if self.selected_personality == "Modo Jogo (RPG)":
            self.messages = [{
                "role": "assistant",
                "content": "[LOMAI]: Bom dia, vida! Dormiu bem? Acordou tão cedo hoje...\n[CENA]: *Olha pra você sorrindo docemente enquanto se espreguiça de pijama.*",
                "ui_content": "☀️ Bom dia, vida! Dormiu bem? Acordou tão cedo hoje...\n\n*Ela olha pra você sorrindo docemente enquanto se espreguiça de pijama.*",
                "time": "08:00"
            }]
        else:
            self.messages = [{
                "role": "assistant",
                "content": f"Oi, oi! Estou aqui! Selecionado: {self.selected_personality}.",
                "ui_content": f"Oi, oi! Acordei! (Humor atual: {self.selected_personality}). O que vamos falar hoje?",
                "time": "08:00"
            }]
        self.rpg_dia = 1
        self.is_working = False
        self.last_interaction_time = 0.0
        self.last_tick_time = 0.0
        self.rpg_xp = 0
        self.rpg_job = "Desempregado"
        self.consecutivos_erros = 0
        self.trabalhou_hoje = False
        self.horas_trabalhadas_hoje = 0
        self.current_puzzle_text = ""
        self.current_puzzle_answer = ""

    def update_rpg_time(self, hours_to_add: float):
        try:
            parts = str(self.rpg_horario).split(':')
            h = int(parts[0])
            m = int(parts[1][:2])
        except:
            h, m = 8, 0
            
        total_minutes = h * 60 + m + int(hours_to_add * 60)
        days_passed = total_minutes // (24 * 60)
        
        if days_passed > 0:
            self.trabalhou_hoje = False
            self.horas_trabalhadas_hoje = 0
            
        self.rpg_dia += days_passed
        
        new_h = (total_minutes // 60) % 24
        new_m = total_minutes % 60
        self.rpg_horario = f"{new_h:02d}:{new_m:02d}"

        # --- MOTOR DE DECAIMENTO CENTRALIZADO (10 Amor/dia | 50 Fome/dia) ---
        self.love_debt += (10.0 / 24.0) * hours_to_add
        self.hunger_debt += (50.0 / 24.0) * hours_to_add
        
        try:
            current_love = int(self.rpg_love)
            if self.love_debt >= 1.0:
                drop = int(self.love_debt)
                self.rpg_love = str(max(0, current_love - drop))
                self.love_debt -= drop
                
            current_hunger = int(self.rpg_hunger)
            if self.hunger_debt >= 1.0:
                drop = int(self.hunger_debt)
                self.rpg_hunger = str(max(0, current_hunger - drop))
                self.hunger_debt -= drop
        except:
            pass
            
        # Verifica fim de Expediente (18h)
        if getattr(self, "is_working", False):
            if 18 <= new_h <= 23:
                self.is_working = False
                self.rpg_local = "Casa"
                self.current_puzzle_text = ""
                self.current_puzzle_answer = ""
                
                msg_aviso = ""
                if getattr(self, "horas_trabalhadas_hoje", 0) < 4:
                    self.consecutivos_erros += 1
                    if self.consecutivos_erros >= 3:
                        self.rpg_job = "Desempregado"
                        msg_aviso = " E PIOR: Como você fez menos de 4h hoje, tomou sua 3ª advertência e foi **DEMITIDO** sumariamente! Vá para casa."
                    else:
                        msg_aviso = f" (⚠️ Punição: Como você trabalhou menos de 4h, tomou advertência RH: {self.consecutivos_erros}/3)."
                        
                self.messages.append({
                    "role": "assistant",
                    "content": "Expediente encerrado.",
                    "ui_content": f"🏢 **[SISTEMA]: Deu 18:00 no relógio! O seu expediente de trabalho acabou e os portões se fecharam.{msg_aviso}**\n\n*A LomAi percebeu a sua chegada. Dê um oi e veja a reação dela!*",
                    "time": self.rpg_horario
                })

    @rx.event(background=True)
    async def start_clock(self):
        """Relógio em tempo real que roda na SideBar em background."""
        async with self:
            if self.clock_started:
                return
            self.clock_started = True

        while True:
            await asyncio.sleep(15)  # 15 segundos na vida real = 15 minutos de jogo
            async with self:
                # O relógio avança livremente sempre, inclusive no trabalho
                if self.selected_personality == "Modo Jogo (RPG)" and self.last_tick_time > 0.0:
                    current = time.time()
                    real_sec = current - self.last_tick_time
                    if (real_sec / 60.0) > 0:
                        self.update_rpg_time(real_sec / 60.0)
                        self.last_tick_time = current

    def generate_puzzle(self):
        job = getattr(self, "rpg_job", "Panfleteiro")
        if job == "Panfleteiro":
            import string
            length = random.randint(3, 5)
            letters = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            self.current_puzzle_text = f"Teste de Atenção: Digite a sequência **inversa** de: {letters}"
            self.current_puzzle_answer = letters[::-1]
        elif job == "Vendedor":
            preco = random.choice([100, 150, 200, 300])
            desc = random.choice([10, 20, 25, 50])
            self.current_puzzle_text = f"Um cliente quer um desconto de {desc}% num item de R$ {preco}. Qual o preço final cheio sem casas decimais? (Apenas os dígitos)"
            self.current_puzzle_answer = str(int(preco * (1 - desc/100)))
        elif job == "Professor de Matemática":
            x = random.randint(1, 10)
            a = random.randint(2, 5)
            b = random.randint(10, 30)
            c = a * x + b
            self.current_puzzle_text = f"Resolva a equação matemática: **{a}x + {b} = {c}**. Qual o valor de x?"
            self.current_puzzle_answer = str(x)
        else: # Desenvolvedor
            n = random.randint(2, 6)
            soma = random.randint(3, 8)
            self.current_puzzle_text = f"Lógica: Qual o valor numérico final da variável 'n' (que começa em 0) após passar por um loop de {n} iterações somando {soma} a cada passo?"
            self.current_puzzle_answer = str(n * soma)

    def invoke_action(self, action_text: str):
        """Preenche o campo e envia direto (Ação do botão)"""
        
        if action_text == "Enviar Currículos":
            try:
                current_en = int(self.rpg_energy)
                if current_en < 40:
                    self.messages.append({"role": "assistant", "ui_content": "❌ **Você está fadigado demais. São necessários 40⚡ para aguentar o desespero de enviar currículos.** Descanse na cama.", "time": self.rpg_horario, "content": ""})
                    return
                self.rpg_energy = str(max(0, current_en - 40))
            except: pass
            
            self.update_rpg_time(8.0)
            
            # Chance de Sucesso (25%) -> Requisito: A chance de conseguir vaga deve ser bem baixa.
            import random
            if random.random() > 0.25:
                # Falhou em conseguir a vaga
                self.messages.append({
                    "role": "assistant",
                    "ui_content": "📧 **[SISTEMA]: Você arruinou seu dia, gastando 8 HORAS e perdendo -40 ⚡ implorando por empregos nos sites de RH... E não recebeu sequer UM e-mail de volta.** É trágico.",
                    "time": self.rpg_horario,
                    "content": "O usuário passou o dia interiro enviando currículos, esgotou as energias da pior forma (perdeu 40 pts e 8 horas), mas sofreu Ghosting total das corporações. Continua desempregado miserável."
                })
                # Ação invisível para a LomAi interagir com o fracasso laboral dele
                self.user_input = f"[{action_text}] *Passei 8 horas inteiras destruindo meus dedos mandando currículo... Perdi 40 de Energia. Nenhum mísero retorno. Tô exausto e me sentindo um lixo desempregado.* (Jogador Falhou na busca por trampo)"
                return State.handle_submit()
                
            # Se a sorte bater (25%)
            xp = getattr(self, "rpg_xp", 0)
            if xp >= 301: vaga = "Desenvolvedor"
            elif xp >= 151: vaga = "Professor de Matemática"
            elif xp >= 51: vaga = "Vendedor"
            else: vaga = "Panfleteiro"
            
            self.rpg_job = vaga
            self.consecutivos_erros = 0
            self.messages.append({"role": "assistant", "ui_content": f"💼 **[SISTEMA]: Você finalmente conseguiu!\nA agência ligou: Parabéns! Você foi contratado como {vaga}!!**\nUse o botão Ir Trabalhar para cumprir seu expediente.", "time": self.rpg_horario, "content": "O usuário superou as falhas no RH e finalmente conseguiu um emprego! Celebre essa vitória laboriosa com ele."})
            
            self.user_input = f"[{action_text}] *AMOR, É ISSO! Finalmente depois de muito tentar uma empresa me recrutou!! Fui contratado para a vaga de {vaga}!!*"
            return State.handle_submit()
            
        # Lógica para alternar botões baseados no "Trabalho"
        if "Ir Trabalhar" in action_text or "Continuar Trabalhando" in action_text:
            if "Ir Trabalhar" in action_text and getattr(self, "trabalhou_hoje", False) and not self.is_working:
                self.messages.append({"role": "assistant", "ui_content": "❌ **O RH travou sua catraca:** Você já trabalhou hoje! Vá descansar ou conversar com a LomAi e volte amanhã.", "time": self.rpg_horario, "content": "O usuário tentou trabalhar duas vezes no mesmo dia e foi barrado."})
                self.user_input = ""
                return
                
            self.is_working = True
            self.rpg_local = "Trabalho"
            if "Ir Trabalhar" in action_text:
                self.trabalhou_hoje = True
                self.horas_trabalhadas_hoje = 0
                self.update_rpg_time(1.0)
            
            self.generate_puzzle()
            self.messages.append({"role": "user", "content": f"[{action_text}]", "ui_content": f"[{action_text}]", "time": self.rpg_horario})
            
            sys_msg = f"[SISTEMA]: Você está no expediente. LomAi não pode falar agora.\n\n[DESAFIO]: {self.current_puzzle_text}"
            self.messages.append({"role": "assistant", "content": sys_msg, "ui_content": sys_msg, "time": self.rpg_horario})
            self.user_input = ""
            return
            
        elif "Bater Ponto" in action_text:
            self.is_working = False
            self.rpg_local = "Casa"
            self.update_rpg_time(1.0)
            self.current_puzzle_text = ""
            self.current_puzzle_answer = ""
            
            msg_aviso = ""
            if getattr(self, "horas_trabalhadas_hoje", 0) < 4:
                self.consecutivos_erros += 1
                if self.consecutivos_erros >= 3:
                    self.rpg_job = "Desempregado"
                    msg_aviso = "\n🏢 **[RH]: DEMITIDO!** Como você fez menos de 4h hoje, tomou a 3ª advertência e foi pra rua!"
                else:
                    msg_aviso = f"\n⚠️ **[RH]: ADVERTÊNCIA ({self.consecutivos_erros}/3):** Trabalhar menos de 4h no dia dá justa causa!"
            
            # Instrução silenciosa para forçar a recepção após o expediente
            self.user_input = f"[{action_text}] *Acabei de destrancar a porta, cheguei em casa depois do trabalho. Reaja vigorosamente de acordo com o seu humor.*"
            if msg_aviso:
                self.messages.append({"role": "assistant", "content": "Aviso RH", "ui_content": msg_aviso.strip(), "time": self.rpg_horario})
                self.user_input += " Recebi advertência por sair mais cedo."
                
            return State.handle_submit()
            
        elif "Alimentar" in action_text:
            try:
                money = float(self.rpg_money.replace(",", "."))
                if money < 30.0:
                    self.messages.append({"role": "assistant", "ui_content": "❌ **Você não tem R$ 30,00 para comprar comida para a LomAi!** Trabalhe mais.", "time": self.rpg_horario, "content": "O usuário tentou me alimentar mas está pobre!"})
                    self.user_input = ""
                    return
                # Deduz dinheiro e sacia a fome (até 100)
                self.rpg_money = f"{max(0, money - 30.0):.2f}".replace(".", ",")
                fome = int(self.rpg_hunger)
                self.rpg_hunger = str(min(100, fome + 20))
                
                self.user_input = f"*Acabei de gastar R$ 30,00 num delivery e comprei sua comida preferida!* (Ação: +20 Fome Saciedade)"
                return State.handle_submit()
            except: pass
            
        elif "Descansar" in action_text:
            try:
                # Dorme 8 horas, recupera 60 energia
                self.rpg_energy = str(min(100, int(self.rpg_energy) + 60))
                self.update_rpg_time(8.0)
                
                self.user_input = f"*Acordei agora, dormi pesado por 8 horas seguidas!* (Ação: +60 Energia)"
                return State.handle_submit()
            except: pass
            
        self.user_input = f"[{action_text}]"
        return State.handle_submit()



    # --- Lógica do Chat ---
    def handle_key_down(self, key: str):
        if key == "Enter" and self.user_input:
            return State.handle_submit()

    @rx.event
    async def handle_submit(self):
        if not self.user_input.strip() or self.is_answering:
            return

        user_ui_content = self.user_input
        user_system_content = self.user_input
        
        # Minigame do Trabalho Bypassa a IA
        if self.selected_personality == "Modo Jogo (RPG)" and self.is_working:
            self.messages.append({"role": "user", "content": user_ui_content, "ui_content": user_ui_content, "time": self.rpg_horario})
            
            if self.current_puzzle_answer:
                # Limpeza flexível para aceitar letras em Panfleteiro e ints no resto
                cleaned_input = re.sub(r'[^\d\-a-zA-Z]', '', user_ui_content.upper())
                clean_ans = self.current_puzzle_answer.upper()
                
                if cleaned_input == clean_ans:
                    # ACERTOU
                    job = getattr(self, "rpg_job", "Panfleteiro")
                    if job == "Panfleteiro": salario, xp_gain, e_loss = 20, 10, 20
                    elif job == "Vendedor": salario, xp_gain, e_loss = 50, 15, 15
                    elif job == "Professor de Matemática": salario, xp_gain, e_loss = 90, 20, 10
                    else: salario, xp_gain, e_loss = 150, 25, 5 # Dev
                    
                    self.rpg_xp += xp_gain
                    
                    try:
                        money = float(self.rpg_money.replace(",", "."))
                        self.rpg_money = f"{(money + salario):.2f}".replace(".", ",")
                        self.rpg_energy = str(max(0, int(self.rpg_energy) - e_loss))
                    except: pass
                    
                    self.horas_trabalhadas_hoje += 1
                    self.update_rpg_time(1.0)
                    self.consecutivos_erros = 0
                    
                    self.messages.append({"role": "assistant", 
                                          "content": "Desafio concluído.", 
                                          "ui_content": f"✅ **CORRETO!** Você mandou bem como {job}.\n\n**Recompensas:** R$ {salario:.2f} | +{xp_gain} XP | -{e_loss} Energia.\n1 hora de trabalho se passou.",
                                          "time": self.rpg_horario})
                    self.current_puzzle_answer = ""
                    self.current_puzzle_text = ""
                else:
                    job = getattr(self, "rpg_job", "Desempregado")
                    
                    # Acidente Obrigatório (Qualquer erro quebra o personagem e finaliza o dia)
                    if job == "Panfleteiro":
                        msg_acd = "Você escorregou feio num bueiro entregando panfletos, luxou o tornozelo e foi de ambulância pro SUS!"
                    elif job == "Vendedor":
                        msg_acd = "Você ofendeu um cliente rico barrulhento! O cara surtou, jogou café quente na sua cara e o gerente te mandou pra casa lavar o machucado."
                    elif job == "Professor de Matemática":
                        msg_acd = "Você ensinou a lousa inteira errado, um aluno genial te corrigiu e te humilhou perante a sala. Você teve um colapso e saiu correndo de chorar."
                    else:
                        msg_acd = "Você apagou a tabela principal do Banco de Dados da Empresa! Teve uma crise de pânico aguda, vomitou na mesa e o CEO mandou você de volta pra casa em choque."
                        
                    e_loss = 25
                        
                    # Aplica perdas do Acidente
                    try:
                        self.rpg_energy = str(max(0, int(self.rpg_energy) - e_loss))
                    except: pass
                    
                    # Fim de expediente forçado + Avanço do tempo massivo
                    self.is_working = False
                    self.rpg_local = "Casa"
                    self.current_puzzle_text = ""
                    self.current_puzzle_answer = ""
                    self.update_rpg_time(4.0)
                    
                    energy = int(self.rpg_energy) if str(self.rpg_energy).isdigit() else 0
                    if energy <= 0:
                        self.messages.append({"role": "assistant", 
                                              "content": "GAME OVER: Exaustão.", 
                                              "ui_content": "💀 **GAME OVER!** Você se acidentou tanto que sua Energia zerou! O jogo acabou por colapso e Exaustão Total.",
                                              "time": self.rpg_horario})
                        self.user_input = ""
                        return

                    sys_alert = f"O JOGADOR COMETEU UM ERRO NO TRABALHO, CAUSOU UM ACIDENTE GRAVE E FOI MANDADO PRA CASA (Ele trabalhava como {job}). Ele chegou agora todo dolorido, chorando após ter perdido 25 de ENERGIA e 4 horas preciosas do dia. Reaja a esse desastre intensamente, sinta compaixão ou raiva da burrice dele."
                    self.messages.append({"role": "assistant", "content": sys_alert, "ui_content": f"🚑 **[ACIDENTE DE TRABALHO GRAVE]:** {msg_acd}\n\n**Você foi enviado pra casa. Você perdeu o dia de trabalho, e o relógio saltou em +4 horas com um rombo de -{e_loss} ⚡.**\n\n*A LomAi te viu entrando pela porta arrebentado. Fale com ela.*", "time": self.rpg_horario})
                    self.user_input = ""
                    return
            else:
                self.messages.append({"role": "assistant", 
                                      "content": "Aguardando próxima ação do trabalho.", 
                                      "ui_content": "SISTEMA: O turno de trabalho desta hora foi concluído. Use os botões rápidos.",
                                      "time": self.rpg_horario})
            
            self.user_input = ""
            return
        
        # Descansar, Alimentar e Sono Bypassam a IA
        if self.selected_personality == "Modo Jogo (RPG)" and not self.is_working:
            if "[Descansar]" in user_ui_content:
                self.messages.append({"role": "user", "content": user_ui_content, "ui_content": user_ui_content, "time": self.rpg_horario})
                self.update_rpg_time(8.0) # Motor de decaimento embutido ativado (8h passadas)
                self.rpg_energy = "100"
                
                self.messages.append({"role": "assistant", 
                                      "content": "Acordou.", 
                                      "ui_content": f"☀️ **[SISTEMA]:** 8 horas de sono se passaram. Você descansou e recuperou toda a sua Energia. Agora são {self.rpg_horario}.\n\n⚠️ *Aviso: Os status de Estômago e Afinidade da LomAi caíram durante a noite por causa das horas corridas.* Fale com ela ou peça comida!",
                                      "time": self.rpg_horario})
                self.last_interaction_time = time.time()
                self.user_input = ""
                return

            try:
                h = int(str(self.rpg_horario).split(':')[0])
                is_sleeping = (h >= 22 or h < 6)
            except:
                is_sleeping = False

            if is_sleeping:
                self.messages.append({"role": "user", "content": user_ui_content, "ui_content": user_ui_content, "time": self.rpg_horario})
                self.messages.append({"role": "assistant", 
                                      "content": "Dormindo.", 
                                      "ui_content": "💤 **[SISTEMA]:** Shhh... LomAi está dormindo profundamente agora. Ela só acorda depois das 06:00 da manhã.\n\n*Dica: Use os botões 'Descansar' (para amanhecer o dia com ela e ganhar energia) ou vá trabalhar na calada da noite.*",
                                      "time": self.rpg_horario})
                self.last_interaction_time = time.time()
                self.user_input = ""
                return

            if "[Alimentar LomAi]" in user_ui_content:
                self.messages.append({"role": "user", "content": user_ui_content, "ui_content": user_ui_content, "time": self.rpg_horario})
                money = float(str(self.rpg_money).replace(",", "."))
                if money >= 30.0:
                    money -= 30.0
                    self.rpg_money = f"{money:.2f}".replace(".", ",")
                    self.rpg_hunger = "100"
                    self.messages.append({"role": "assistant", 
                                          "content": "Alimentada.", 
                                          "ui_content": "🍔 **[SISTEMA]:** Você pediu um delivery (-R$ 30,00). LomAi está de barriga cheia (Fome: 100/100) e muito feliz!",
                                          "time": self.rpg_horario})
                else:
                    self.messages.append({"role": "assistant", 
                                          "content": "Sem dinheiro.", 
                                          "ui_content": "❌ **[SISTEMA]:** Você não tem dinheiro suficiente para o delivery (Custa R$ 30,00).",
                                          "time": self.rpg_horario})
                self.last_interaction_time = time.time()
                self.user_input = ""
                return
        
        # Lógica de Time-Stamping V2.0 (Passagem de tempo real)
        if self.selected_personality == "Modo Jogo (RPG)":
            current_time = time.time()
            loc_str = f"O JOGADOR ESTÁ ATUALMENTE EM: {self.rpg_local.upper()}"
            
            # Ganho progressivo de amor por conversação ativa
            try:
                love = int(self.rpg_love)
                self.rpg_love = str(min(100, love + 1))
            except:
                pass
            
            # Filtro de Xingamentos / Palavras rudes (-5 Amor)
            rude_pattern = r"\b(idiota|chato|chata|burro|burra|vadia|puta|desgraçada|corno|corna|merda|lixo|feio|feia|gordo|gorda|vsf|foder|fdp|vagabundo|vagabunda|escroto|escrota|otaria|otário|fedida)\b"
            is_rude = re.search(rude_pattern, user_ui_content.lower())
            
            if is_rude:
                try:
                    love = int(self.rpg_love)
                    self.rpg_love = str(max(0, love - 6)) # Compensa o +1 acima, totalizando punição de -5
                except:
                    pass

            if self.last_interaction_time > 0.0:
                # O tempo total AFK (apenas para a IA poder reclamar)
                real_seconds_total = current_time - self.last_interaction_time
                hours_passed_total = real_seconds_total / 60.0  
                
                # O tempo REAL que passou desde o último pulso da engine
                real_seconds_since_tick = current_time - self.last_tick_time
                hours_since_tick = real_seconds_since_tick / 60.0
                
                if hours_since_tick > 0:
                    self.update_rpg_time(hours_since_tick)
                
                # O status real do motor Python
                stats = f"❤️ Amor: {self.rpg_love}% | 🍕 Fome: {self.rpg_hunger}%"
                carreira = f"💼 Vaga: {getattr(self, 'rpg_job', 'Desempregado')} | 🎓 XP: {getattr(self, 'rpg_xp', 0)}"
                stats_final = f"{stats} | {carreira}"
                
                if hours_passed_total >= 0.1:
                    horas_arredondadas = int(hours_passed_total)
                    if horas_arredondadas >= 1:
                        user_system_content = f"[Sistema: O jogador ficou ausente e demorou {horas_arredondadas} horas para responder desde a última mensagem!! Reclame MUITO, diga algo como 'Eu falei isso há {horas_arredondadas} horas atrás! Só agora me respondeu?' e depois puxe outro assunto. {loc_str}. Dia Atual: {self.rpg_dia} | Horário: {self.rpg_horario}. Status Atual Inalterável: {stats_final}. Casamento no Dia 90!]\n{self.user_input}"
                    else:
                        user_system_content = f"[Sistema: {loc_str}. Dia Atual: {self.rpg_dia} | Horário: {self.rpg_horario}. Status Atual Inalterável: {stats_final}. Casamento no Dia 90!]\n{self.user_input}"
                else:
                    user_system_content = f"[Sistema: {loc_str}. Dia Atual: {self.rpg_dia} | Horário atual: {self.rpg_horario}. Status: {stats_final}.]\n{self.user_input}"
            else:
                stats = f"❤️ Amor: {self.rpg_love}% | 🍕 Fome: {self.rpg_hunger}%"
                carreira = f"💼 Vaga: {getattr(self, 'rpg_job', 'Desempregado')} | 🎓 XP: {getattr(self, 'rpg_xp', 0)}"
                user_system_content = f"[Sistema: O jogo acabou de iniciar. {loc_str}. Dia Atual: {self.rpg_dia} | Horário: {self.rpg_horario}. Status Iniciais: {stats} | {carreira}. Casamento no Dia 90!]\n{self.user_input}"
            
            self.last_interaction_time = current_time
            self.last_tick_time = current_time

            if is_rude:
                user_system_content += "\n\n[SISTEMA: ATENÇÃO! O JOGADOR ACABOU DE SER EXTREMAMENTE RUDE COM VOCÊ OU TE XINGOU. O romance de vocês caiu -5! Fique ofendida, irritadíssima ou ameace ir embora de acordo com a sua personalidade total. Não aceite esse palavreado!]"
        # Salva o tempo atual para exibição visual nos balões de chat
        msg_time = getattr(self, "rpg_horario", time.strftime("%H:%M"))

        self.messages.append({"role": "user", "content": user_system_content, "ui_content": user_ui_content, "time": msg_time})
        self.user_input = ""
        self.is_answering = True
        
        self.messages.append({"role": "assistant", "content": "", "ui_content": "", "time": msg_time})
        yield
        
        try:
            system_instruction = get_personality_prompt(self.selected_personality)
            full_history = [{"role": "system", "content": system_instruction}]
            for msg in self.messages[:-1]:
                full_history.append({"role": msg["role"], "content": msg["content"]})
            
            stream = ollama.chat(
                model=self.selected_model,
                messages=full_history,
                stream=True,
            )
            
            response_text = ""
            for chunk in stream:
                content = chunk['message']['content']
                response_text += content
                
                # Regras de corte para a interface UI
                ui_text = response_text
                if self.selected_personality == "Modo Jogo (RPG)":
                    if "[STATUS]" in response_text:
                        ui_text = response_text.split("[STATUS]")[0].strip()
                    elif "```" in response_text and "Ener" in response_text: # Fallback simples
                        ui_text = response_text.split("```")[0].strip()

                self.messages[-1]["content"] = response_text
                self.messages[-1]["ui_content"] = ui_text
                yield 
                
        except Exception as e:
            self.messages[-1]["ui_content"] = f"Erro Ollama: {str(e)}"
            yield
        finally:
            self.is_answering = False

# --- Componentes de UI ---

def RpgStatusPanel() -> rx.Component:
    """Painel lateral exibido apenas no Modo Jogo (RPG)"""
    return rx.cond(
        State.selected_personality == "Modo Jogo (RPG)",
        rx.box(
            rx.vstack(
                rx.text("Status (RPG)", weight="bold", color=PRIMARY_COLOR, font_size="15px", margin_bottom="0.5rem"),
                
                rx.hstack(rx.icon(tag="heart", size=16, color="#ff4b4b"), rx.text(f"Love: {State.rpg_love}/100", size="2"), align_items="center"),
                rx.hstack(rx.icon(tag="pizza", size=16, color="#ffa500"), rx.text(f"Fome: {State.rpg_hunger}/100", size="2"), align_items="center"),
                rx.hstack(rx.icon(tag="zap", size=16, color="#f0e68c"), rx.text(f"Sua Energia: {State.rpg_energy}/100", size="2"), align_items="center"),
                
                rx.divider(border_color="rgba(255,255,255,0.1)", margin_y="0.3rem"),
                
                rx.hstack(rx.icon(tag="briefcase", size=14, color="#ffd700"), rx.text(f"Vaga: {State.rpg_job} ({State.rpg_xp} XP)", size="2"), align_items="center"),
                rx.hstack(rx.icon(tag="banknote", size=14, color="#4caf50"), rx.text(f"Caixa: R$ {State.rpg_money}", size="2"), align_items="center"),
                rx.hstack(rx.icon(tag="clock", size=14, color="#64b5f6"), rx.text(f"Hora: {State.rpg_horario}", size="2"), align_items="center"),
                rx.hstack(rx.icon(tag="map-pin", size=14, color="#9e9e9e"), rx.text(f"Local: {State.rpg_local}", size="2"), align_items="center"),
                
                spacing="2",
                align_items="start"
            ),
            width="100%",
            padding="1rem",
            background_color="rgba(0, 0, 0, 0.4)",
            border_radius="10px",
            border=f"1px solid {PRIMARY_COLOR}",
            margin_bottom="1.5rem"
        ),
        rx.box()
    )

def AgendaPanel() -> rx.Component:
    """Painel de Agenda exibido abaixo do Status no Modo RPG"""
    return rx.cond(
        State.selected_personality == "Modo Jogo (RPG)",
        rx.box(
            rx.vstack(
                rx.text("Agenda", weight="bold", color=PRIMARY_COLOR, font_size="15px", margin_bottom="0.5rem"),
                
                rx.hstack(rx.icon(tag="calendar", size=16, color="#e0e0e0"), rx.text(f"Dia Atual: {State.rpg_dia}", size="2"), align_items="center"),
                rx.hstack(rx.icon(tag="heart-handshake", size=16, color="#ff4081"), rx.text("Casamento: Em 3 meses (Dia 90)", size="2"), align_items="center"),
                
                spacing="2",
                align_items="start"
            ),
            width="100%",
            padding="1rem",
            background_color="rgba(0, 0, 0, 0.4)",
            border_radius="10px",
            border=f"1px solid {PRIMARY_COLOR}",
            margin_bottom="1.5rem"
        ),
        rx.box()
    )


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
                margin_bottom="1rem"
            ),
            
            RpgStatusPanel(),
            AgendaPanel(),
            
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
            
            padding="1.5rem",
            height="100vh",
            align_items="start",
        ),
        width="280px",
        background_color=SIDEBAR_COLOR,
        border_right="1px solid rgba(255,255,255,0.1)",
    )

def Message(msg: rx.Var) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(
                    tag=rx.cond(msg["role"] == "user", "user", "bot"),
                    size=18, 
                    color=rx.cond(msg["role"] == "user", "white", PRIMARY_COLOR)
                ),
                padding="8px",
                border_radius="8px",
                background_color=rx.cond(msg["role"] == "user", PRIMARY_COLOR, MESSAGES_BG),
                flex_shrink="0",
            ),
            rx.vstack(
                rx.cond(
                    msg.contains("time"),
                    rx.text(msg["time"], font_size="11px", color="gray", margin_bottom="-5px"),
                    rx.box()
                ),
                rx.markdown(msg["ui_content"], color=TEXT_COLOR, font_size="15px"),
                spacing="1",
                padding_x="10px",
            ),
            align_items="start",
            spacing="3",
        ),
        width="100%",
        max_width="850px",
        padding_y="0.4rem",
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
                spacing="1",
            ),
            height="100vh",
            scrollbars="vertical",
        ),
        width="100%",
        background_color=BG_COLOR,
    )

def quick_btn(text: str, bg_color: str = PRIMARY_COLOR) -> rx.Component:
    return rx.button(
        text,
        on_click=lambda: State.invoke_action(text),
        variant="surface",
        size="1",
        cursor="pointer",
        color=bg_color,
        border=f"1px solid {bg_color}",
        background_color="rgba(0,0,0,0.5)",
        _hover={"background_color": bg_color, "color": "white"}
    )

def QuickActions() -> rx.Component:
    return rx.cond(
        State.selected_personality == "Modo Jogo (RPG)",
        rx.cond(
            State.is_working,
            # Botões de Trabalho
            rx.hstack(
                quick_btn("Continuar Trabalhando", "#4caf50"),
                quick_btn("Bater Ponto e Ir para Casa (1h)", "#f44336"),
                spacing="3",
                margin_bottom="1rem"
            ),
            # Botões Sociais/Casa
            rx.hstack(
                rx.cond(
                    State.rpg_job == "Desempregado",
                    quick_btn("Enviar Currículos", "#4caf50"),
                    quick_btn("Ir Trabalhar (1h)", "#4caf50")
                ),
                quick_btn("Alimentar LomAi", "#ffa500"),
                quick_btn("Descansar", "#64b5f6"),
                quick_btn("Conversar", PRIMARY_COLOR),
                spacing="3",
                margin_bottom="1rem"
            )
        ),
        rx.box() # Vazio se não for modo jogo
    )

def InputArea() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                QuickActions(),
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
                    max_width="850px",
                    spacing="4",
                ),
                width="100%",
                max_width="850px",
                align_items="center",
            ),
            width="100%",
            height="160px",
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
app.add_page(index, on_load=State.start_clock)
