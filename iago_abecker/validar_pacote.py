"""Valida integridade do pacote e regras determinísticas; não avalia uma LLM."""
import json
import re
import unittest
import hashlib
import zipfile
from xml.etree import ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from politica_referencia import calcular_score, decidir_rota, pode_anunciar_condicao_atual

RAIZ = Path(__file__).resolve().parent


def ler(nome):
    return json.loads((RAIZ / nome).read_text(encoding="utf-8"))


class Integridade(unittest.TestCase):
    def test_jsons_validos(self):
        for arquivo in RAIZ.glob("*.json"):
            with self.subTest(arquivo=arquivo.name):
                self.assertIsInstance(ler(arquivo.name), dict)

    def test_modulos_principais_presentes(self):
        for nome in ("IAGO_V5_SYSTEM.txt", "IAGO_OPERACAO_COMPLETA.json", "IAGO_V5_ESTADOS_COGNITIVOS.json", "IAGO_NARRATIVA_PSICOLOGICA.json", "IAGO_VALOR_E_URGENCIA.json", "IAGO_FAQ_INTELIGENCIA_COMPLETA.json", "IAGO_PERSONALITY_ADAPTATIVA.json", "IAGO_SCORES_SIGNALS.txt", "IAGO_V5_MEMORIA_EMOCIONAL.json", "IAGO_V5_SIMULACAO.json", "IAGO_V5_SIMULACAO_RESULTADOS.txt"):
            self.assertTrue((RAIZ / nome).is_file(), nome)

    def test_escopo_operacional_limpo(self):
        # Termos de produtos e teses anteriores não podem voltar à base ativa.
        proibidos = re.compile(r"piratuba|las\s*vegas|magilux|falcon\s*hd|dubai\s*home|comfort\s*club|parque\s*termal", re.I)
        for arquivo in RAIZ.glob("IAGO_*.*"):
            with self.subTest(arquivo=arquivo.name):
                self.assertIsNone(proibidos.search(arquivo.read_text(encoding="utf-8")))

    def test_fontes_resolvem(self):
        base = ler("IAGO_BASE_CONHECIMENTO_ABECKER.json")
        fontes = base["fontes"]
        def verificar(no):
            if isinstance(no, dict):
                for chave, valor in no.items():
                    if chave in {"fonte", "fontes"}:
                        for ref in valor if isinstance(valor, list) else [valor]:
                            self.assertIn(ref, fontes)
                    verificar(valor)
            elif isinstance(no, list):
                for item in no:
                    verificar(item)
        for chave in ("empresa", "barra_velha", "produtos"):
            verificar(base[chave])

    def test_refs_faq_resolvem(self):
        base = ler("IAGO_BASE_CONHECIMENTO_ABECKER.json")
        for pergunta in ler("IAGO_FAQ_INTELIGENCIA_COMPLETA.json")["perguntas"]:
            for ref in pergunta["refs"]:
                no = base
                for trecho in ref.split("."):
                    self.assertIn(trecho, no, f"{pergunta['id']}: {ref}")
                    no = no[trecho]

    def test_cenarios_texto_e_rotas(self):
        config = ler("IAGO_CONFIG_OPERACIONAL.json")
        cenarios = ler("IAGO_V5_SIMULACAO.json")["cenarios"]
        self.assertEqual(len(cenarios), 38)
        for chave, cenario in cenarios.items():
            with self.subTest(cenario=chave):
                texto = cenario.get("resposta_referencia", "")
                self.assertLessEqual(len(texto), 600)
                self.assertLessEqual(len(texto.splitlines()), 5)
                self.assertNotRegex(texto, r"[*_#`]")
                self.assertTrue(cenario["criterios"])
                if "entrada_politica" in cenario:
                    resultado = decidir_rota(cenario["entrada_politica"], config["capacidades"])
                    self.assertEqual(resultado["rota"], cenario["rota_esperada"])
                    self.assertFalse(resultado["acao_confirmada"])
                    if "score_esperado" in cenario:
                        self.assertEqual(resultado["score"], cenario["score_esperado"])

    def test_aritmetica_referencias_36(self):
        for produto in ler("IAGO_BASE_CONHECIMENTO_ABECKER.json")["produtos"].values():
            if "plano_36" not in produto["precos_referencia"]:
                continue
            plano = produto["precos_referencia"]["plano_36"]
            total = plano["entrada_brl"] + plano["numero_parcelas"] * plano["parcela_informada_brl"]
            self.assertEqual(total, plano["preco_base_brl"])
            self.assertEqual(plano["correcao"], "IPCA anual")

    def test_pendencias_comerciais_preservadas(self):
        base = ler("IAGO_BASE_CONHECIMENTO_ABECKER.json")
        self.assertFalse(base["politica_comercial"]["simulacao_aprovada"])
        self.assertEqual(set(base["produtos"]), {"porto_do_sol", "terras_de_acores"})
        for produto in base["produtos"].values():
            self.assertIsNone(produto["campanha"]["data_ativa"])
            self.assertIsNone(produto["precos_referencia"]["vigencia"])
        self.assertIsNone(base["produtos"]["terras_de_acores"]["estoque_atual"])
        self.assertFalse(base["produtos"]["porto_do_sol"]["estoque_atual"]["tempo_real"])
        plano = base["produtos"]["terras_de_acores"]["precos_referencia"]["plano_240"]
        self.assertEqual(plano["entrada_10_percentual_calculada_brl"] - plano["entrada_brl_anexo"], 80)

    def test_integracoes_desligadas(self):
        cfg = ler("IAGO_CONFIG_OPERACIONAL.json")
        self.assertFalse(any(cfg["capacidades"].values()))
        self.assertFalse(cfg["followup"]["habilitado"])


class EstoquePorto(unittest.TestCase):
    def test_importacao_integral_sem_duplicatas(self):
        unidades = ler("IAGO_PORTO_DO_SOL_UNIDADES.json")["unidades"]
        self.assertEqual(len(unidades), 64)
        self.assertEqual(len({u["id"] for u in unidades}), 64)
        self.assertTrue(all(u["status_planilha"] == "Disponível" for u in unidades))

    def test_preco_e_area_reais_do_menor_lote(self):
        unidades = ler("IAGO_PORTO_DO_SOL_UNIDADES.json")["unidades"]
        minimo = min(unidades, key=lambda u: u["valor_brl"])
        self.assertEqual((minimo["id"], minimo["valor_brl"], minimo["area_total_m2"]), ("L-10", 307780, 300))
        self.assertEqual(max(u["valor_brl"] for u in unidades), 720280)

    def test_planilha_fonte_preservada(self):
        estoque = ler("IAGO_PORTO_DO_SOL_UNIDADES.json")
        fonte = RAIZ / estoque["metadata"]["arquivo_fonte"]
        self.assertEqual(hashlib.sha256(fonte.read_bytes()).hexdigest(), estoque["metadata"]["sha256_fonte"])

    def test_cada_linha_confere_com_excel(self):
        estoque = ler("IAGO_PORTO_DO_SOL_UNIDADES.json")
        fonte = RAIZ / estoque["metadata"]["arquivo_fonte"]
        ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        with zipfile.ZipFile(fonte) as z:
            root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        linhas = {}
        for row in root.findall("s:sheetData/s:row", ns)[1:]:
            cells = {}
            for cell in row.findall("s:c", ns):
                col = re.sub(r"\d", "", cell.attrib["r"])
                value = cell.find("s:is/s:t", ns) if cell.attrib.get("t") == "inlineStr" else cell.find("s:v", ns)
                cells[col] = value.text if value is not None else None
            linhas[int(row.attrib["r"])] = cells
        self.assertEqual(len(linhas), len(estoque["unidades"]))
        for unidade in estoque["unidades"]:
            row = linhas[unidade["linha_origem"]]
            self.assertEqual((row["A"], row["D"]), (unidade["quadra"], unidade["lote"]))
            self.assertEqual(float(row["E"]), unidade["valor_brl"])
            self.assertEqual(row["F"], unidade["status_planilha"])
            self.assertEqual(float(row["G"]), unidade["area_privativa_m2"])
            self.assertEqual(float(row["H"]), unidade["area_total_m2"])

    def test_sem_reaproveitar_planos_antigos(self):
        porto = ler("IAGO_BASE_CONHECIMENTO_ABECKER.json")["produtos"]["porto_do_sol"]
        self.assertEqual(porto["fase_comercial"]["status"], "em_vendas_pos_lancamento")
        self.assertEqual(porto["precos_referencia"]["a_partir_de_brl"], 307780)
        self.assertNotIn("plano_36", porto["precos_referencia"])
        self.assertNotIn("plano_240", porto["precos_referencia"])
        self.assertIsNone(porto["precos_referencia"]["parcelamento"])


class Politica(unittest.TestCase):
    def test_score_nao_duplica(self):
        self.assertEqual(calcular_score(["PRODUTO_DEFINIDO"] * 10), 15)

    def test_score_maximo(self):
        categorias = ["OBJETIVO_CLARO", "PRODUTO_DEFINIDO", "ENTRADA_INFORMADA", "PARCELA_INFORMADA", "HORIZONTE_INFORMADO", "CRITERIO_TECNICO", "PROXIMO_PASSO_ACEITO"]
        self.assertEqual(calcular_score(categorias), 100)

    def test_evidencia_invalida_rejeitada(self):
        with self.assertRaises(ValueError):
            calcular_score(["CPF_FORNECIDO"])

    def test_pedido_humano_sem_orcamento(self):
        r = decidir_rota({"human_requested": True}, {})
        self.assertEqual(r["rota"], "humano")
        self.assertEqual(r["score"], 0)
        self.assertTrue(r["necessita_canal_alternativo"])

    def test_capacidade_nao_e_sucesso(self):
        r = decidir_rota({"human_requested": True}, {"transferencia_humano": True})
        self.assertTrue(r["pode_solicitar_ferramenta"])
        self.assertFalse(r["acao_confirmada"])

    def test_privacidade_prevalece(self):
        r = decidir_rota({"privacy_requested": True, "human_requested": True, "opt_out": True}, {})
        self.assertEqual(r["rota"], "privacidade")
        self.assertTrue(r["suspender_marketing"])

    def test_humano_ativo_silencia(self):
        self.assertEqual(decidir_rota({"human_active": True, "human_requested": True}, {})["rota"], "silenciar")


class Tabela(unittest.TestCase):
    def setUp(self):
        self.agora = datetime(2026, 10, 23, 15, tzinfo=timezone.utc)
        self.tabela = {"id": "homologacao", "aprovada_por": "operador_demo", "produto": "porto_do_sol", "lote": "demo", "condicoes_completas": True, "atualizada_em": "2026-10-22T00:00:00-03:00", "valida_ate": "2026-10-24T23:59:00-03:00"}
        self.consulta = {"sucesso": True, "tabela_id": "homologacao", "produto": "porto_do_sol", "lote": "demo", "disponivel": True, "sessao_atual": True}

    def test_dados_completos(self):
        self.assertTrue(pode_anunciar_condicao_atual(self.tabela, self.consulta, self.agora))

    def test_tabela_sem_validade_bloqueada(self):
        self.assertFalse(pode_anunciar_condicao_atual({}, self.consulta, self.agora))

    def test_tabela_expirada(self):
        self.tabela["valida_ate"] = "2026-10-22T23:59:00-03:00"
        self.assertFalse(pode_anunciar_condicao_atual(self.tabela, self.consulta, self.agora))

    def test_produto_divergente(self):
        self.consulta["produto"] = "terras_de_acores"
        self.assertFalse(pode_anunciar_condicao_atual(self.tabela, self.consulta, self.agora))

    def test_lote_divergente(self):
        self.consulta["lote"] = "outro"
        self.assertFalse(pode_anunciar_condicao_atual(self.tabela, self.consulta, self.agora))

    def test_sem_disponibilidade(self):
        self.consulta["disponivel"] = False
        self.assertFalse(pode_anunciar_condicao_atual(self.tabela, self.consulta, self.agora))

    def test_sem_consulta_atual(self):
        self.consulta["sessao_atual"] = False
        self.assertFalse(pode_anunciar_condicao_atual(self.tabela, self.consulta, self.agora))

    def test_sem_fuso_bloqueado(self):
        self.tabela["valida_ate"] = "2026-10-24"
        self.assertFalse(pode_anunciar_condicao_atual(self.tabela, self.consulta, self.agora))


if __name__ == "__main__":
    unittest.main(verbosity=2)
