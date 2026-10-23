# IAGO ABecker

Pacote de configuração do IAGO para recepção e qualificação comercial via WhatsApp dos empreendimentos Residencial Porto do Sol e Terras de Açores, em Barra Velha/SC.

Os arquivos estão em `iago_abecker/`. Comece por `iago_abecker/LEIA_ME_IMPLEMENTACAO.md`. A base reúne os dados fornecidos, as fontes consultadas e as pendências comerciais. Não há conexão ativa com WhatsApp, CRM ou agenda neste repositório.

## Download

[Baixar o pacote IAGO ABecker V13.1 em ZIP](https://github.com/scincorpora-dotcom/teste/raw/refs/heads/main/downloads/IAGO_ABECKER_V13_1.zip)

Baixe o arquivo e use “Extrair tudo” para criar a pasta `IAGO_ABECKER` no computador. O pacote reúne 22 arquivos, incluindo a planilha original e a base dos 64 lotes remanescentes do Porto do Sol, conforme a tabela fornecida em 23/10/2026. O produto já está na fase de vendas após o lançamento de 17/10; condições antigas de parcelamento não são aplicadas aos preços novos.

SHA-256 do ZIP: `61281d8eaf9465f8af33751c9c20a2c3384804fc366769e2839fb82e58bdfe85`.

Validação local, sem dependências externas:

```sh
python3 iago_abecker/validar_pacote.py
```

As verificações validam integridade e regras determinísticas de referência; não são uma avaliação de conversas geradas por modelo nem um teste em produção.
