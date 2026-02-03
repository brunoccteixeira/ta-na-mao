"""
Testes para o modo Acompanhante Digital.

Testa perfis de acompanhante, checklist pre-visita,
registro de atendimento e orientacao passo-a-passo.
"""

import pytest
from app.agent.tools.acompanhante_digital import (
    iniciar_modo_acompanhante,
    gerar_checklist_pre_visita,
    registrar_atendimento,
    obter_orientacao_passo_a_passo,
    PerfilAcompanhante,
)


class TestIniciarModoAcompanhante:
    """Testes para iniciar modo acompanhante."""

    def test_perfil_acs(self):
        """ACS deve ter permissoes especificas."""
        result = iniciar_modo_acompanhante("acs")
        assert result["modo_ativo"] is True
        assert result["perfil"] == "acs"
        assert len(result["permissoes"]) > 0
        assert len(result["restricoes"]) > 0

    def test_perfil_assistente_social(self):
        """Assistente social deve ter consulta completa."""
        result = iniciar_modo_acompanhante("assistente_social")
        assert result["modo_ativo"] is True
        assert result["perfil"] == "assistente_social"
        assert any("completa" in p.lower() for p in result["permissoes"])

    def test_perfil_familiar(self):
        """Familiar deve ter restricoes de dados sensiveis."""
        result = iniciar_modo_acompanhante("familiar")
        assert result["modo_ativo"] is True
        assert result["perfil"] == "familiar"
        assert any("cpf" in r.lower() for r in result["restricoes"])

    def test_perfil_invalido(self):
        """Perfil invalido deve retornar erro."""
        result = iniciar_modo_acompanhante("invalido")
        assert "erro" in result
        assert "perfis_disponiveis" in result

    def test_conteudo_cidadao(self):
        """Deve ter conteudo para o cidadao."""
        result = iniciar_modo_acompanhante("acs")
        assert "conteudo_cidadao" in result
        assert len(result["conteudo_cidadao"]) > 10

    def test_passos_sugeridos(self):
        """Deve ter passos sugeridos."""
        result = iniciar_modo_acompanhante("acs")
        assert "passos_sugeridos" in result
        assert len(result["passos_sugeridos"]) >= 4

    def test_acs_tem_passo_registrar(self):
        """ACS deve ter passo adicional de registrar visita."""
        result = iniciar_modo_acompanhante("acs")
        passos = result["passos_sugeridos"]
        titulos = [p["titulo"] for p in passos]
        assert any("registrar" in t.lower() for t in titulos)

    def test_com_nome_acompanhante(self):
        """Deve aceitar nome do acompanhante."""
        result = iniciar_modo_acompanhante("acs", nome_acompanhante="Maria")
        assert result["modo_ativo"] is True

    def test_com_municipio(self):
        """Deve aceitar municipio."""
        result = iniciar_modo_acompanhante("acs", municipio="Sao Paulo")
        assert result["municipio"] == "Sao Paulo"


class TestGerarChecklistPreVisita:
    """Testes para checklist de pre-visita."""

    def test_checklist_cadunico_basico(self):
        """CadUnico basico deve ter documentos obrigatorios."""
        result = gerar_checklist_pre_visita("CADUNICO")
        assert len(result["documentos_obrigatorios"]) >= 4
        assert len(result["dicas_preparacao"]) >= 3
        assert result["tempo_estimado"]

    def test_checklist_bpc(self):
        """BPC deve mencionar laudo medico."""
        result = gerar_checklist_pre_visita("BPC")
        docs = " ".join(result["documentos_obrigatorios"])
        assert "laudo" in docs.lower()

    def test_checklist_com_filhos(self):
        """Com filhos deve adicionar documentos extras."""
        result = gerar_checklist_pre_visita("CADUNICO", tem_filhos=True)
        extras = " ".join(result["documentos_extras"])
        assert "nascimento" in extras.lower() or "vacinacao" in extras.lower()

    def test_checklist_gestante(self):
        """Gestante deve ter documentos de pre-natal."""
        result = gerar_checklist_pre_visita("CADUNICO", gestante=True)
        extras = " ".join(result["documentos_extras"])
        assert "pre-natal" in extras.lower() or "gravidez" in extras.lower()

    def test_checklist_deficiencia(self):
        """Deficiencia deve pedir laudo com CID."""
        result = gerar_checklist_pre_visita("BPC", deficiencia=True)
        extras = " ".join(result["documentos_extras"])
        assert "cid" in extras.lower() or "laudo" in extras.lower()

    def test_checklist_personalizado_nome(self):
        """Deve personalizar com nome do cidadao."""
        result = gerar_checklist_pre_visita("CADUNICO", nome_cidadao="Joao")
        assert "Joao" in result["saudacao"]

    def test_formato_imprimivel(self):
        """Deve ter formato imprimivel."""
        result = gerar_checklist_pre_visita("CADUNICO")
        impressao = result["formato_imprimivel"]
        assert "CHECKLIST" in impressao
        assert "[ ]" in impressao

    def test_fluxo_cras(self):
        """Deve descrever o que acontece no CRAS."""
        result = gerar_checklist_pre_visita("CADUNICO")
        assert len(result["o_que_acontece_no_cras"]) >= 4

    def test_bpc_tempo_maior(self):
        """BPC deve ter tempo estimado maior."""
        result = gerar_checklist_pre_visita("BPC")
        assert "2" in result["tempo_estimado"] or "3" in result["tempo_estimado"]

    def test_familia_grande_dica_extra(self):
        """Familia grande deve ter dica sobre levar docs de todos."""
        result = gerar_checklist_pre_visita("CADUNICO", composicao_familiar=5)
        dicas = " ".join(result["dicas_preparacao"])
        assert "5" in dicas or "todas" in dicas.lower()


class TestRegistrarAtendimento:
    """Testes para registro de atendimento."""

    def test_registro_basico(self):
        """Deve registrar atendimento com sucesso."""
        result = registrar_atendimento(
            perfil_acompanhante="acs",
            acoes_realizadas=["consulta", "checklist"],
            resultado="beneficio_encontrado",
        )
        assert result["registrado"] is True
        assert "id_atendimento" in result

    def test_registro_com_municipio(self):
        """Deve incluir municipio no registro."""
        result = registrar_atendimento(
            perfil_acompanhante="assistente_social",
            acoes_realizadas=["consulta"],
            resultado="encaminhado_cras",
            municipio="Recife",
        )
        assert result["resumo"]["municipio"] == "Recife"

    def test_cpf_eh_hasheado(self):
        """CPF deve ser hasheado, nunca armazenado."""
        result = registrar_atendimento(
            perfil_acompanhante="acs",
            acoes_realizadas=["consulta"],
            resultado="consulta_realizada",
            cpf_cidadao="529.982.247-25",
        )
        # O resultado nao deve conter o CPF em texto plano
        result_str = str(result)
        assert "529.982.247-25" not in result_str
        assert "52998224725" not in result_str

    def test_registro_resumo(self):
        """Deve ter resumo do atendimento."""
        result = registrar_atendimento(
            perfil_acompanhante="familiar",
            acoes_realizadas=["consulta", "checklist", "encaminhamento"],
            resultado="encaminhado_cras",
        )
        assert result["resumo"]["total_acoes"] == 3
        assert result["resumo"]["resultado"] == "encaminhado_cras"


class TestOrientacaoPassoAPasso:
    """Testes para orientacao passo-a-passo."""

    def test_consultar_beneficios_passo_1(self):
        """Primeiro passo de consultar beneficios."""
        result = obter_orientacao_passo_a_passo("CONSULTAR_BENEFICIOS", 1)
        assert result["passo_atual"] == 1
        assert result["total_passos"] >= 3
        assert "titulo" in result
        assert "conteudo_cidadao" in result

    def test_fazer_cadunico_passos(self):
        """Fazer CadUnico deve ter passos."""
        result = obter_orientacao_passo_a_passo("FAZER_CADUNICO", 1)
        assert result["total_passos"] >= 3

    def test_pedir_remedio_passos(self):
        """Pedir remedio deve ter passos."""
        result = obter_orientacao_passo_a_passo("PEDIR_REMEDIO", 1)
        assert result["total_passos"] >= 3

    def test_pedir_bpc_passos(self):
        """Pedir BPC deve ter passos."""
        result = obter_orientacao_passo_a_passo("PEDIR_BPC", 1)
        assert result["total_passos"] >= 4

    def test_progresso(self):
        """Deve mostrar progresso."""
        result = obter_orientacao_passo_a_passo("CONSULTAR_BENEFICIOS", 2)
        assert result["progresso"] == f"2/{result['total_passos']}"

    def test_proximo_passo_verdadeiro(self):
        """Deve indicar se tem proximo passo."""
        result = obter_orientacao_passo_a_passo("CONSULTAR_BENEFICIOS", 1)
        assert result["proximo_passo"] is True

    def test_ultimo_passo_falso(self):
        """Ultimo passo deve indicar que nao tem proximo."""
        # Pegar total de passos
        result = obter_orientacao_passo_a_passo("CONSULTAR_BENEFICIOS", 1)
        total = result["total_passos"]
        # Ir para ultimo
        result = obter_orientacao_passo_a_passo("CONSULTAR_BENEFICIOS", total)
        assert result["proximo_passo"] is False

    def test_passo_invalido(self):
        """Passo invalido deve retornar erro."""
        result = obter_orientacao_passo_a_passo("CONSULTAR_BENEFICIOS", 99)
        assert "erro" in result

    def test_objetivo_invalido(self):
        """Objetivo invalido deve retornar erro."""
        result = obter_orientacao_passo_a_passo("INVALIDO", 1)
        assert "erro" in result
        assert "objetivos_disponiveis" in result

    def test_instrucao_acompanhante(self):
        """Passo deve ter instrucao para acompanhante."""
        result = obter_orientacao_passo_a_passo("CONSULTAR_BENEFICIOS", 1)
        assert len(result["instrucao_acompanhante"]) > 0
