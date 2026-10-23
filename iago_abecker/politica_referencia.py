"""Regras determinísticas de referência para a integração do IAGO.

Não interpreta linguagem natural, chama LLM, grava CRM ou envia WhatsApp.
A plataforma deve extrair e validar os sinais antes de chamar estas funções.
"""
from datetime import datetime

PESOS = {
    "OBJETIVO_CLARO": 15,
    "PRODUTO_DEFINIDO": 15,
    "ENTRADA_INFORMADA": 15,
    "PARCELA_INFORMADA": 15,
    "HORIZONTE_INFORMADO": 10,
    "CRITERIO_TECNICO": 10,
    "PROXIMO_PASSO_ACEITO": 20,
}


def calcular_score(evidencias):
    """Evidências são categorias explícitas já validadas; duplicatas não somam."""
    categorias = set(evidencias)
    desconhecidas = categorias - PESOS.keys()
    if desconhecidas:
        raise ValueError("Categorias de evidência desconhecidas")
    return min(100, sum(PESOS[chave] for chave in categorias))


def decidir_rota(sinais, capacidades):
    """Roteia pedidos estruturados. Não confirma execução de nenhuma ação."""
    score = calcular_score(sinais.get("evidence", []))
    if sinais.get("privacy_requested"):
        rota, capacidade = "privacidade", "registro_privacidade"
    elif sinais.get("opt_out"):
        rota, capacidade = "encerrar", None
    elif sinais.get("human_active"):
        rota, capacidade = "silenciar", None
    elif sinais.get("human_requested"):
        rota, capacidade = "humano", "transferencia_humano"
    elif sinais.get("support_requested"):
        rota, capacidade = "pos_venda", "transferencia_humano"
    elif sinais.get("action_requested"):
        rota = "acao_comercial"
        capacidade = "agenda" if sinais["action_requested"] == "visita" else "crm"
    elif score >= 86:
        if sinais.get("contact_permission") or "PROXIMO_PASSO_ACEITO" in sinais.get("evidence", []):
            rota, capacidade = "humano", "transferencia_humano"
        else:
            rota, capacidade = "pedir_aceite", None
    else:
        rota, capacidade = "atender", None
    silenciado = rota in {"silenciar", "encerrar", "privacidade"}
    pode_solicitar = bool(capacidade and capacidades.get(capacidade, False))
    return {
        "rota": rota,
        "score": score,
        "suspender_marketing": silenciado or rota in {"humano", "pos_venda", "acao_comercial"},
        "pode_solicitar_ferramenta": pode_solicitar,
        "necessita_canal_alternativo": bool(capacidade and not pode_solicitar),
        "acao_confirmada": False,
    }


def _data_aware(valor):
    if not isinstance(valor, str):
        return None
    try:
        data = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return None
    return data if data.tzinfo is not None and data.utcoffset() is not None else None


def pode_anunciar_condicao_atual(tabela, consulta, agora):
    """Gate mínimo: sem lote, aprovação, vigência e consulta atual, falha fechado.

    Confiança da fonte e correção dos valores precisam ser validadas pelo serviço
    comercial. Esta função não substitui essas validações.
    """
    if agora.tzinfo is None or agora.utcoffset() is None:
        raise ValueError("O horário atual deve incluir fuso")
    inicio = _data_aware(tabela.get("atualizada_em"))
    fim = _data_aware(tabela.get("valida_ate"))
    if not inicio or not fim or not inicio <= agora <= fim:
        return False
    obrigatorios = ("id", "aprovada_por", "produto", "lote", "condicoes_completas")
    if not all(tabela.get(chave) for chave in obrigatorios):
        return False
    return bool(
        consulta.get("sucesso") is True
        and consulta.get("tabela_id") == tabela["id"]
        and consulta.get("produto") == tabela["produto"]
        and consulta.get("lote") == tabela["lote"]
        and consulta.get("disponivel") is True
        and consulta.get("sessao_atual") is True
    )
