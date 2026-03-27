# 🤖 LomAi - Interface de Chat Local para LLMs

Uma interface moderna, rápida e elegante estilo **ChatGPT** desenvolvida para rodar modelos de linguagem (LLMs) localmente através do **Ollama**. Desenvolvido com **Reflex (Python)** para uma experiência web premium e responsiva.

![Reflex Version](https://img.shields.io/badge/Reflex-0.8+-blueviolet)
![Ollama Support](https://img.shields.io/badge/Ollama-Local-blue)
![Theme](https://img.shields.io/badge/Theme-Dark-black)

---

## ✨ Funcionalidades

- 💬 **Interface Estilo GPT**: Chat centralizado, limpo e com suporte a Markdown.
- ⚡ **Respostas em Tempo Real**: Streaming de mensagens (texto aparece enquanto é gerado).
- 🎨 **Design Premium**: Tema escuro com cores HSL (roxo vibrante) e animações suaves.
- 🛠️ **Configuração de Modelos**: Troque entre modelos instalados (ex: `qwen2.5:3b`, `llama3`) diretamente pela barra lateral.
- 🧹 **Limpeza de Histórico**: Botão para iniciar uma nova conversa rapidamente.

---

## 🚀 Como Começar

### 1. Pré-requisitos

Certifique-se de ter os seguintes softwares instalados:

- [Python 3.10+](https://www.python.org/downloads/)
- [Ollama](https://ollama.com/) instalado e rodando no sistema.
- Modelos baixados no Ollama (ex: `ollama pull qwen2.5:3b`).

### 2. Instalação das Dependências

Abra o terminal na pasta raiz do projeto (`LomAi/`) e execute:

```powershell
pip install -r requirements.txt
```

### 3. Executando a Interface

Inicie o servidor de desenvolvimento do Reflex:

```powershell
reflex run
```

*Na primeira execução, o Reflex irá configurar o ambiente de frontend (Bun/Node.js). Aguarde até que o terminal mostre "App running at: http://localhost:3000".*

---

## 🛠️ Estrutura do Projeto

- `rxconfig.py`: Configurações globais do Reflex (está otimizado para não mostrar warnings).
- `chat_ui/`: Pasta contendo o código-fonte da aplicação Python.
  - `chat_ui.py`: Lógica do Estado (State) e componentes visuais.
  - `__init__.py`: Ponto de entrada que exporta o app para o Reflex.
- `.web/`: (Gerado automaticamente) Contém o frontend compilado em Next.js.
- `.states/`: (Gerado automaticamente) Armazena persistência de estados.

---

## 🗒️ Notas de Uso

- **Ollama**: O backend do chat depende do processo `ollama serve` estar ativo. Se o script não encontrar o Ollama, ele exibirá um erro de conexão na bolha do chat.
- **Personalização**: Você pode alterar as cores principais editando as constantes `BG_COLOR` e `PRIMARY_COLOR` no topo do arquivo `chat_ui/chat_ui.py`.

---

## ⚖️ Licença

Este projeto está sob a licença [MIT](LICENSE).

---
*Desenvolvido com ❤️ usando Reflex.*
