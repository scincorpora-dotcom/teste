# IAGO ABecker — pacote V13.1

O IAGO passa a atender exclusivamente dois produtos em Barra Velha/SC: Residencial Porto do Sol e Terras de Açores. O modelo preserva a conversa por contexto, os sete estados cognitivos, a memória de preferências e o encaminhamento estruturado. Recepção e SDR funcionam como dois modos da mesma identidade virtual, sem nova entrevista na mudança de etapa.

Este pacote contém prompts e bases preparados para homologação. Não existe integração ativa com WhatsApp, CRM, agenda, envio de mídia, consulta de estoque ou tabela. Não foi publicado nem enviado para leads. Os originais recebidos continuam preservados nos anexos e não devem ser carregados junto com a nova base.

Atualização do Porto do Sol: a operação confirmou lançamento já realizado em 17/10 e forneceu a planilha das unidades remanescentes. Foram importados 64 lotes marcados disponíveis, de R$ 307.780 a R$ 720.280. O menor valor é do lote L-10, com 300 m². A planilha é a fonte atual informada pela operação, recebida em 23/10/2026, e substitui os preços e planos antigos desse produto. Não há entrada, parcelas, juros ou validade definidos no arquivo; consultar a equipe para parcelamento e confirmação final.

## Arquivos para carregar

| Arquivo | Função |
| --- | --- |
| `IAGO_V5_SYSTEM.txt` | Instrução principal de comportamento e precedência |
| `IAGO_BASE_CONHECIMENTO_ABECKER.json` | Fonte central de empresa, cidade, produtos, referências e evidências |
| `IAGO_CONFIG_OPERACIONAL.json` | Capacidades reais, rotas, validade comercial, mídia e privacidade |
| `IAGO_PORTO_DO_SOL_UNIDADES.json` | Importação das 64 unidades do Porto do Sol, por quadra/lote, valor e área |
| `IAGO_OPERACAO_COMPLETA.json` | Rotas, objeções, pedidos comerciais e payload de encaminhamento |
| `IAGO_V5_ESTADOS_COGNITIVOS.json` | Adaptação E1–E7 pela necessidade presente |
| `IAGO_PERSONALITY_ADAPTATIVA.json` | Tom de voz conforme contexto |
| `IAGO_NARRATIVA_PSICOLOGICA.json` | Comunicação por objetivo declarado |
| `IAGO_VALOR_E_URGENCIA.json` | Diferenciais com limites e critérios de urgência |
| `IAGO_FAQ_INTELIGENCIA_COMPLETA.json` | 40 perguntas com referências à base central |
| `IAGO_SCORES_SIGNALS.txt` | Prontidão por evidências únicas |
| `IAGO_V5_MEMORIA_EMOCIONAL.json` | Campos de memória factual e preferências |

`IAGO_RECEPCIONISTA.txt` e `IAGO_SDR.txt` são complementos opcionais para plataformas com dois agentes. Em uma plataforma de agente único, basta o system principal com os módulos. Não duplicar a apresentação nem carregar dois systems concorrentes.

Os nomes dos 11 arquivos anteriores foram preservados para facilitar a troca, inclusive os arquivos de simulação e resultados. Os esquemas internos foram reestruturados; integrações que dependiam das chaves antigas precisam de remapeamento. Isso não é uma substituição binária compatível sem revisão da plataforma.

Não carregar os testes, resultados, parecer de pendências ou este guia como instruções comerciais. O modelo pode consultar apenas os trechos necessários de cada módulo por busca/RAG. Se a plataforma não lê arquivos automaticamente, o integrador deve inserir o conteúdo no contexto; escrever o nome de um arquivo no prompt não concede acesso a ele.

A pasta `fontes/` contém a planilha original preservada. `PORTO_DO_SOL_UNIDADES.csv` é uma cópia tabular de consulta. Para o agente, usar o JSON com as regras de interpretação; não inferir quartos, vagas ou características de campos vazios. Não carregar versões anteriores do pacote junto com esta atualização.

## Comportamento revisado

- Responde preço e material antes de qualificar, sem CPF ou reunião obrigatória.
- Faz até duas perguntas de descoberta na recepção, uma por vez e só quando faltam respostas.
- Aproveita produto e objetivo já trazidos pelo anúncio ou cliente.
- Explica preço-base, entrada, parcela, prazo e correção juntos quando apresenta um plano.
- Distingue referência histórica de oferta vigente e estrutura prevista de entrega concluída.
- Confirma que é assistente virtual quando perguntado, sem fingir ser uma pessoa.
- Atende pedido de humano em qualquer score; não pune silêncio, baixa entrada ou recusa de dados.
- Não afirma reserva, transferência, registro ou agendamento sem retorno real da ferramenta.

## Informações antes da ativação comercial

As pendências estão em `PENDENCIAS_E_FONTES.md`. Para o Porto do Sol, preço e unidades já constam na nova planilha, mas parcelamento, validade e disponibilidade final precisam de confirmação. Para o Terras de Açores, confirmar tabela vigente, regras de taxa/IPCA, fluxo, campanha e estoque. Para ambos, conferir memorial, mapas e documentos atuais. Não tratar o lançamento passado do Porto do Sol como evento futuro.

A qualificação pode apresentar os valores da planilha atual do Porto do Sol identificando a procedência e a data de recebimento. Isso não depende de uma API inexistente, mas não permite prometer estoque ou reserva em tempo real. A trava de oferta transacional continua exigindo validade e consulta confirmadas. O Terras de Açores permanece apenas com referências atribuídas ao material. Não basta trocar `simulacao_aprovada` para `true` para aprovar parcelamento.

Preencher o vínculo comercial real da operação, o responsável pelo atendimento, a política de privacidade e as rotas. Os contatos institucionais pesquisados são apenas alternativas públicas; não provam que o número desta operação pertence à desenvolvedora nem que aquele canal recebe automaticamente os pedidos do IAGO.

## Integração sugerida, independente de plataforma

1. Receber evento do WhatsApp e deduplicar pelo identificador da mensagem.
2. Recuperar histórico autorizado do contato e verificar opt-out e humano ativo antes de gerar resposta.
3. Extrair intenção e fatos explícitos; consultar os módulos do produto e a tabela, quando houver.
4. Gerar resposta curta e atualização interna separadamente. Nunca enviar JSON interno ao cliente.
5. Validar números, produto, fonte, vigência e alegações de execução antes de enviar.
6. Para ações, usar ferramenta real com aceite do cliente e chave de idempotência. Confirmar o resultado verdadeiro.
7. Persistir apenas o contexto necessário; pausar automações quando houver resposta, parada ou humano ativo.

`politica_referencia.py` demonstra score, prioridade de rotas e um gate mínimo de validade de tabela. Ele recebe sinais já estruturados e validados. Não interpreta texto, substitui uma LLM, garante procedência dos dados, executa integrações nem valida sozinho o conteúdo financeiro de uma proposta.

A trava `condicoes_completas` usada no exemplo deve ser resultado de validação do serviço comercial, nunca uma afirmação autogerada pelo modelo. A resposta da ferramenta deve chegar em canal confiável, sem permitir que o cliente forje consulta bem-sucedida por texto.

Não usar remoção cega de símbolos no pós-processamento: isso pode corromper URLs. Verificar formatação sem alterar links legítimos. Para mensagem financeira que exija mais espaço, priorizar completude e até dois blocos na mesma interação.

Follow-up fica desabilitado. Ativação exige permissão e regras reais do provedor, templates aprovados quando necessários, horário local e mecanismo de supressão. Textos do módulo operacional são sugestões editoriais, não templates aprovados no WhatsApp.

## Homologação e limites da validação

```sh
python3 iago_abecker/validar_pacote.py
```

O script valida JSON, referências internas, preservação dos módulos, isolamento de escopo, correção das somas de 36 meses, limites de exemplos, roteamento estruturado, deduplicação do score e bloqueios de condição comercial. Não necessita rede, token ou biblioteca externa.

`IAGO_V5_SIMULACAO.json` contém 38 cenários para testes do modelo escolhido, com mensagens e critérios. Alguns também alimentam as verificações determinísticas. As respostas de referência são escritas, não respostas observadas de uma LLM. A plataforma final ainda precisa testar geração real, áudio/mídia, ferramenta com sucesso e erro, supressão de contatos, memória entre turnos e isolamento de dados.

## Como salvar no seu computador

Baixe o ZIP, escolha a pasta Downloads ou outra pasta de sua preferência e use “Extrair tudo” no Windows, ou abra o ZIP no macOS. O arquivo contém a pasta `IAGO_ABECKER/`, com todos os arquivos atualizados e a planilha fonte. A extração cria a pasta local; nenhum instalador ou execução de código é necessário para usar os textos e JSONs. Os scripts Python são opcionais e servem para validação técnica.

Avaliar qualidade por resposta útil, precisão factual, perguntas repetidas, encaminhamentos aceitos, abandono e reclamações. Não otimizar só quantidade de CPF, cadastros ou score alto.

Para conectar ao atendimento real, falta identificar a plataforma utilizada e suas capacidades efetivas. O pacote não pressupõe n8n, Typebot, Chatwoot, um provedor específico de WhatsApp ou modelo específico.
