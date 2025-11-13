# Comandos de Voz do Assistente

Este documento detalha todos os comandos de voz reconhecidos pelo assistente, divididos por categoria.

## 
 Comandos Gerais

Comandos básicos para interação com arquivos, aplicativos e macros salvas.

* `[nome da macro]`
    * **Ação:** Executa uma macro que já foi gravada.
    * *Exemplo:* "fazer login"

* `abrir o whatsapp` / `abra o whatsapp`
    * **Ação:** Abre o aplicativo desktop do WhatsApp e o traz para o foco.

* `avise [contato] que [mensagem]`
    * **Ação:** Abre o WhatsApp, procura o contato e envia a mensagem.
    * *Exemplo:* "avise o joão que estou chegando"
    * *(Variações: "mande para [contato] dizendo que...", "envie [contato] que...")*

* `(abrir/selecionar) [arquivo] em [pasta]`
    * **Ação:** Abre ou seleciona um arquivo em uma pasta conhecida. A ação "abrir" é o padrão se nenhum verbo for dito.
    * *Exemplo 1:* "abrir zero zero ponto pdf em documentos"
    * *Exemplo 2:* "hornet mp3 em downloads" (Irá "abrir")
    * *Exemplo 3:* "selecione 0003146 em documento"

## Comandos de Visão (OCR)

Comandos que usam a visão computacional (OCR) para interagir com o que está visível na tela.

* `copiar de [texto A] até [texto B]`
    * **Ação:** Lê a tela, encontra o `[texto A]`, rola a tela se necessário até encontrar o `[texto B]`, e copia todo o texto entre eles.

* `selecionar de [texto A] até [texto B]`
    * **Ação:** Clica e arrasta o mouse do `[texto A]` até o `[texto B]`.

* `clicar em [nome da imagem]` / `clicar na imagem [nome da imagem]`
    * **Ação:** Procura um recorte de imagem salvo na pasta `img/` (ex: `botao.png`) e clica nele.
    * *Exemplo:* "clicar em caixa_branca"

* `digite [texto]`
    * **Ação:** Tenta encontrar uma caixa de texto conhecida na tela e digita o texto.
    * *Exemplo:* "digite meu email arroba gmail ponto com"

* `colar`
    * **Ação:** Executa "Ctrl + V".

* `copiar seleção`
    * **Ação:** Executa "Ctrl + C".

* `espere [X] segundos`
    * **Ação:** Pausa a execução da macro ou comando pelo tempo especificado.
    * *Exemplo:* "espere 3 segundos"

* `criar arquivo de texto com nome [nome] e conteúdo [conteúdo]`
    * **Ação:** Cria um arquivo `.txt` no diretório do projeto.
    * *Exemplo:* "criar arquivo de texto com nome lista e conteúdo item 1"

* **(Matemática e Lógica)**
    * `some [A] e [B]`
    * `subtraia [A] e [B]`
    * `multiplique [A] e [B]`
    * `dividido por [A] e [B]`
    * `compare [A] [maior que/menor que/igual a] [B]`

## Modo Administrador (Gerenciamento de Macros)

Comandos para criar, apagar e gerenciar macros.

* `modo 0012`
    * **Ação:** Ativa o "Modo Administrador" para permitir a gravação de macros.

* `sair do modo admin`
    * **Ação:** Desativa o modo administrador.

* `aprenda a [nome da macro]`
    * **Ação:** Inicia uma gravação manual de cliques do mouse e teclas. Pressione **Ctrl + Esc** para parar a gravação.
    * *Exemplo:* "aprenda a fazer login"

* `aprenda a [nome da macro] abrindo o arquivo de nome [caminho]`
    * **Ação:** Inicia a gravação e abre um arquivo específico antes de gravar as ações.

* `aprenda a [nome da macro] clicando em [nome da imagem]`
    * **Ação:** Cria uma "Macro Visual" de passo único que clica na imagem especificada.
    * *Exemplo:* "aprenda a pesquisar clicando em icone_pesquisa"

* `aprenda a [nome da macro] pelos passos [passo 1] e [passo 2]...`
    * **Ação:** Cria uma "Macro Híbrida" que executa outros comandos ou macros em sequência.
    * *Exemplo:* "aprenda a rotina matinal pelos passos abrir o whatsapp e clicar em joão"

* `apagar macro [nome da macro]`
    * **Ação:** Exclui permanentemente uma macro salva.
    * *Exemplo:* "apagar macro fazer login"

* `sobrescrever macro [nome da macro]`
    * **Ação:** Inicia uma nova gravação manual para substituir uma macro existente.

---

### Apêndice: Pastas Reconhecidas

O assistente reconhece os seguintes "apelidos" para pastas ao usar comandos de arquivo:

* `download`
* `downloads`
* `transferência`
* `transferências`
* `documento`
* `documentos`
* `área de trabalho`