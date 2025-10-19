# Assistente Virtual Offline com Whisper

Este projeto é uma interface gráfica (GUI) para um assistente de voz que utiliza o modelo Whisper da OpenAI para transcrição de áudio de alta precisão, rodando 100% offline em CPU.

## Funcionalidades

* **Reconhecimento de Voz Offline:** Nenhuma conexão com a internet é necessária após a configuração inicial.
* **Alta Precisão:** Utiliza um modelo Whisper (medium) fine-tuned para o português, otimizado para rodar em CPU com a biblioteca CTranslate2.
* **Detecção de Fala:** Usa uma lógica de limiar de volume para detectar o início e o fim da fala, gravando apenas quando o usuário está falando.
* **Interface Simples:** Uma janela simples para iniciar/parar a escuta e visualizar o texto transcrito.

## Configuração do Ambiente (Setup)

Siga estes passos para configurar o projeto em uma nova máquina Windows.

### 1. Pré-requisitos

Antes de instalar as dependências do Python, dois componentes de sistema são necessários:

* **Microsoft C++ Redistributable:** Essencial para executar as bibliotecas C++ subjacentes. Baixe o instalador `VC_redist.x64.exe` do [site oficial da Microsoft](https://learn.microsoft.com/pt-br/cpp/windows/latest-supported-vc-redist) e instale-o. **Reinicie o computador após a instalação.**

* **FFmpeg:** Necessário para o processamento de áudio por bibliotecas dependentes.
    1.  Baixe a versão `ffmpeg-release-essentials.zip` de [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/).
    2.  Extraia o conteúdo para um local permanente (ex: `C:\ffmpeg`).
    3.  Adicione a pasta `bin` do FFmpeg (ex: `C:\ffmpeg\bin`) ao `Path` das variáveis de ambiente do Windows.

### 2. Configuração do Projeto

1.  **Clone o Repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd jarvis
    ```

2.  **Crie e Ative o Ambiente Virtual:**
    ```powershell
    
    python -m venv .venv

    .\.venv\Scripts\Activate.ps1
    ```

3.  **Instale as Dependências Python:**
    ```powershell
    pip install -r requirements.txt
    ```

### 3. Download e Conversão do Modelo (Passo Único)

Este passo requer uma conexão com a internet e só precisa ser feito uma vez. Ele irá baixar o modelo Whisper (~1.5 GB) e convertê-lo para um formato otimizado.

1.  No terminal com o ambiente ativado, execute o seguinte comando:
    ```powershell
    ct2-transformers-converter --model pierreguillou/whisper-medium-portuguese --output_dir whisper-medium-pt-ct2 --quantization float16
    ```
2.  Isso criará uma pasta `whisper-medium-pt-ct2` no seu projeto. Esta pasta é o seu modelo de IA local e offline.

## Como Usar

1.  **Ajuste o Limite de Silêncio (Opcional):**
    * Se o assistente não estiver detectando sua fala corretamente, pode ser necessário ajustar o `SILENCE_THRESHOLD` no arquivo `main.py`. Use o script `utils/calibrator.py` (se o tiver mantido) para encontrar um valor ideal para o seu microfone e ambiente.

2.  **Execute o Programa:**
    * Com o ambiente virtual ativado, rode o `main.py`:
        ```powershell
        python main.py
        ```
    * A interface gráfica será aberta. Use os botões para iniciar e parar a escuta.

## Estrutura do Projeto

* `main.py`: Ponto de entrada da aplicação, contém a interface gráfica (GUI).
* `utils/listener.py`: Classe principal que gerencia o microfone, a detecção de fala e a comunicação com o modelo Whisper.
* `whisper-medium-pt-ct2/`: Pasta contendo o modelo de IA otimizado para execução local.
* `requirements.txt`: Lista de dependências Python para o projeto.