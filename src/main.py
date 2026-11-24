import json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

def run():
    # Inicia o gerenciador de contexto do Playwright em modo síncrono
    with sync_playwright() as p:
        # Abre o Google Chrome oficial instalado no Ubuntu com janela maximizada e sem flag básica de automação
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        # Cria um contexto de navegação limpo permitindo que a janela use a resolução total da tela
        context = browser.new_context(no_viewport=True)
        # Abre uma nova aba no navegador
        page = context.new_page()

        # Acessa a página inicial do Google
        page.goto("https://www.google.com")
        # Localiza a barra de pesquisa do Google, digita "youtube" e pressiona Enter
        campo_google = page.locator('[name="q"]')
        campo_google.fill("youtube")
        campo_google.press("Enter")

        # Aguarda e clica no primeiro resultado orgânico que possui um título principal (h3)
        primeiro_resultado = page.locator('#search a:has(h3)').first
        primeiro_resultado.click()

        # Aguarda a barra de busca do YouTube ficar visível e preenche o termo pesquisado
        campo_yt = page.locator('input[name="search_query"]')
        campo_yt.wait_for(state="visible")
        campo_yt.fill("playwright chrash course")

        # Localiza o botão de lupa (compatível com o layout clássico e novo do YouTube) e clica nele
        botao_pesquisar = page.locator(
            'button#search-icon-legacy, button.ytSearchboxComponentSearchButton'
        ).first
        botao_pesquisar.click()

        # Aguarda a listagem de resultados e clica no título do primeiro vídeo tradicional (ignorando anúncios/Shorts)
        primeiro_video = page.locator('ytd-video-renderer a#video-title').first
        primeiro_video.wait_for(state="visible")
        primeiro_video.click()

        # Aguarda a navegação para a URL do vídeo e a renderização do bloco principal de metadados
        page.wait_for_url("**/watch?v=*")
        titulo_locator = page.locator('ytd-watch-metadata #title h1')
        titulo_locator.wait_for(state="visible")

        # Registra a data e a hora exatas em que o vídeo foi aberto
        data_hora_abertura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Captura o título do vídeo removendo quebras de linha e espaços nas extremidades
        titulo_video = titulo_locator.inner_text().strip()

        # Aguarda e captura o nome do canal que publicou o vídeo
        canal_locator = page.locator('ytd-watch-metadata ytd-channel-name a').first
        canal_locator.wait_for(state="visible")
        nome_canal = canal_locator.inner_text().strip()

        # Aguarda o botão de "Gostei" carregar e extrai o número de likes exibido na interface
        likes_locator = page.locator(
            'ytd-watch-metadata like-button-view-model button, '
            'ytd-watch-metadata segmented-like-dislike-button-view-model button'
        ).first
        likes_locator.wait_for(state="visible")
        numero_likes = likes_locator.inner_text().strip() or "0"

        # Organiza os dados capturados em um dicionário Python
        dados_video = {
            "titulo": titulo_video,
            "canal": nome_canal,
            "likes": numero_likes,
            "aberto_em": data_hora_abertura
        }

        # Resolve o caminho absoluto do diretório do main.py para salvar o JSON exatamente no mesmo nível
        caminho_json = Path(__file__).resolve().parent / "dados_video.json"

        # Escreve os dados no arquivo JSON preservando acentuação (UTF-8) e com indentação legível
        with open(caminho_json, "w", encoding="utf-8") as arquivo:
            json.dump(dados_video, arquivo, ensure_ascii=False, indent=4)

        # Fecha o navegador e encerra a execução do programa imediatamente após salvar
        browser.close()

if __name__ == "__main__":
    run()