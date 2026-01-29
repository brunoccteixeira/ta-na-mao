"""Tool para preparar pedido de medicamentos.

Orquestra o fluxo:
1. Cria pedido no banco
2. Envia WhatsApp para farmacia
3. Retorna status para cidadao
"""

import uuid
import random
import string
import logging
from typing import List, Dict, Optional

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pedido import Pedido, StatusPedido
from app.agent.tools.enviar_whatsapp import enviar_pedido_farmacia
from app.agent.tools.buscar_farmacia import buscar_farmacia

logger = logging.getLogger(__name__)


def _gerar_numero_pedido() -> str:
    """Gera numero curto do pedido: PED-XXXXX."""
    chars = string.digits
    numero = "".join(random.choices(chars, k=5))
    return f"PED-{numero}"


def _buscar_farmacia_por_id(farmacia_id: str, ibge_code: str) -> Optional[Dict]:
    """Busca dados da farmacia pelo ID."""
    resultado = buscar_farmacia(ibge_code=ibge_code)
    if not resultado.get("encontrados"):
        return None

    for farmacia in resultado.get("farmacias", []):
        if farmacia.get("id") == farmacia_id:
            return farmacia

    return None


def preparar_pedido(
    cpf: str,
    nome: str,
    telefone: str,
    medicamentos: List[Dict],
    farmacia_id: str,
    ibge_code: str,
    receita_url: Optional[str] = None
) -> dict:
    """Cria pedido e envia para farmacia via WhatsApp.

    Esta tool cria um pedido de medicamentos e notifica a farmacia
    para preparar antes do cidadao chegar (estilo iFood).

    Args:
        cpf: CPF do cidadao (11 digitos, sem formatacao)
        nome: Nome completo do cidadao
        telefone: WhatsApp do cidadao para notificacoes
        medicamentos: Lista de medicamentos
            [{"nome": "Losartana", "dosagem": "50mg", "quantidade": 30}]
        farmacia_id: ID da farmacia escolhida
        ibge_code: Codigo IBGE do municipio
        receita_url: URL da foto da receita (opcional)

    Returns:
        dict: {
            "sucesso": True/False,
            "pedido_numero": "PED-12345",
            "pedido_id": "uuid",
            "status": "PENDENTE",
            "farmacia": {
                "nome": "Drogasil Vila Mariana",
                "endereco": "Rua X, 123",
                "whatsapp": "11999999999"
            },
            "mensagem": "Pedido enviado! Aguarde confirmacao...",
            "previsao": "A farmacia vai confirmar em ate 30 minutos",
            "erro": "mensagem de erro se falhar"
        }

    Example:
        >>> preparar_pedido(
        ...     cpf="12345678900",
        ...     nome="Maria Silva",
        ...     telefone="11999999999",
        ...     medicamentos=[{"nome": "Losartana", "dosagem": "50mg"}],
        ...     farmacia_id="drogasil_vila_mariana",
        ...     ibge_code="3550308"
        ... )
    """
    try:
        # 1. Buscar dados da farmacia
        farmacia = _buscar_farmacia_por_id(farmacia_id, ibge_code)
        if not farmacia:
            return {
                "sucesso": False,
                "erro": f"Farmacia '{farmacia_id}' nao encontrada no municipio."
            }

        # Verificar se farmacia tem WhatsApp
        farmacia_whatsapp = farmacia.get("whatsapp")
        if not farmacia_whatsapp:
            return {
                "sucesso": False,
                "erro": f"Farmacia '{farmacia.get('nome')}' nao tem WhatsApp cadastrado."
            }

        # 2. Criar pedido no banco
        pedido_id = str(uuid.uuid4())
        pedido_numero = _gerar_numero_pedido()

        # Obter sessao do banco
        db: Session = next(get_db())

        try:
            pedido = Pedido(
                id=pedido_id,
                numero=pedido_numero,
                cpf_cidadao=cpf,
                nome_cidadao=nome,
                telefone_cidadao=telefone,
                farmacia_id=farmacia_id,
                farmacia_nome=farmacia.get("nome"),
                farmacia_whatsapp=farmacia_whatsapp,
                medicamentos=medicamentos,
                receita_url=receita_url,
                status=StatusPedido.PENDENTE.value
            )

            db.add(pedido)
            db.commit()
            db.refresh(pedido)

            logger.info(f"Pedido criado: {pedido_numero}")

        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao criar pedido no banco: {e}")
            return {
                "sucesso": False,
                "erro": f"Erro ao criar pedido: {str(e)}"
            }

        # 3. Enviar WhatsApp para farmacia
        resultado_whatsapp = enviar_pedido_farmacia(
            farmacia_whatsapp=farmacia_whatsapp,
            pedido_numero=pedido_numero,
            cidadao_nome=nome,
            cidadao_cpf_mascarado=pedido.cpf_mascarado,
            medicamentos_texto=pedido.medicamentos_texto
        )

        if resultado_whatsapp.get("enviado"):
            # Salvar SID do Twilio
            pedido.twilio_sid_farmacia = resultado_whatsapp.get("sid")
            db.commit()

            return {
                "sucesso": True,
                "pedido_numero": pedido_numero,
                "pedido_id": pedido_id,
                "status": StatusPedido.PENDENTE.value,
                "farmacia": {
                    "nome": farmacia.get("nome"),
                    "endereco": farmacia.get("endereco"),
                    "bairro": farmacia.get("bairro"),
                    "whatsapp": farmacia_whatsapp
                },
                "medicamentos": medicamentos,
                "mensagem": f"Pedido {pedido_numero} enviado para {farmacia.get('nome')}!",
                "previsao": "A farmacia vai confirmar em ate 30 minutos. Voce recebera uma mensagem quando estiver pronto!",
                "proximos_passos": [
                    "Aguarde a confirmacao da farmacia",
                    "Voce recebera uma mensagem quando o pedido estiver pronto",
                    "Leve documento com foto e receita para retirar"
                ]
            }
        else:
            # WhatsApp falhou - atualizar status
            pedido.status = StatusPedido.CANCELADO.value
            pedido.observacoes = f"Falha ao enviar WhatsApp: {resultado_whatsapp.get('erro')}"
            db.commit()

            return {
                "sucesso": False,
                "pedido_numero": pedido_numero,
                "erro": f"Nao consegui enviar mensagem para a farmacia: {resultado_whatsapp.get('erro')}",
                "sugestao": "Tente escolher outra farmacia ou ligue diretamente."
            }

    except Exception as e:
        logger.error(f"Erro ao preparar pedido: {e}")
        return {
            "sucesso": False,
            "erro": f"Erro inesperado: {str(e)}"
        }


def consultar_pedido(pedido_numero: str = None, pedido_id: str = None) -> dict:
    """Consulta status de um pedido.

    Args:
        pedido_numero: Numero do pedido (ex: "PED-12345")
        pedido_id: UUID do pedido

    Returns:
        dict: {
            "encontrado": True/False,
            "pedido": {...},
            "status_texto": "Seu pedido esta sendo preparado..."
        }
    """
    if not pedido_numero and not pedido_id:
        return {"encontrado": False, "erro": "Informe o numero ou ID do pedido"}

    db: Session = next(get_db())

    try:
        if pedido_numero:
            pedido = db.query(Pedido).filter(Pedido.numero == pedido_numero).first()
        else:
            pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

        if not pedido:
            return {
                "encontrado": False,
                "erro": "Pedido nao encontrado"
            }

        # Texto amigavel por status
        status_textos = {
            StatusPedido.PENDENTE.value: "Aguardando confirmacao da farmacia...",
            StatusPedido.CONFIRMADO.value: "A farmacia confirmou! Estao preparando seus medicamentos.",
            StatusPedido.PRONTO.value: "PRONTO! Seus medicamentos estao esperando. Va buscar!",
            StatusPedido.RETIRADO.value: "Pedido ja foi retirado. Obrigado!",
            StatusPedido.CANCELADO.value: "Pedido foi cancelado.",
            StatusPedido.EXPIRADO.value: "Pedido expirou (nao retirado no prazo)."
        }

        return {
            "encontrado": True,
            "pedido": {
                "numero": pedido.numero,
                "status": pedido.status,
                "farmacia": pedido.farmacia_nome,
                "medicamentos": pedido.medicamentos,
                "criado_em": pedido.criado_em.isoformat() if pedido.criado_em else None,
                "confirmado_em": pedido.confirmado_em.isoformat() if pedido.confirmado_em else None,
                "pronto_em": pedido.pronto_em.isoformat() if pedido.pronto_em else None
            },
            "status_texto": status_textos.get(pedido.status, "Status desconhecido")
        }

    except Exception as e:
        logger.error(f"Erro ao consultar pedido: {e}")
        return {
            "encontrado": False,
            "erro": f"Erro ao consultar: {str(e)}"
        }


def listar_pedidos_cidadao(cpf: str, apenas_ativos: bool = True) -> dict:
    """Lista pedidos de um cidadao.

    Args:
        cpf: CPF do cidadao
        apenas_ativos: Se True, retorna apenas pedidos pendentes/confirmados/prontos

    Returns:
        dict: {
            "total": 3,
            "pedidos": [...]
        }
    """
    db: Session = next(get_db())

    try:
        query = db.query(Pedido).filter(Pedido.cpf_cidadao == cpf)

        if apenas_ativos:
            status_ativos = [
                StatusPedido.PENDENTE.value,
                StatusPedido.CONFIRMADO.value,
                StatusPedido.PRONTO.value
            ]
            query = query.filter(Pedido.status.in_(status_ativos))

        pedidos = query.order_by(Pedido.criado_em.desc()).all()

        return {
            "total": len(pedidos),
            "pedidos": [
                {
                    "numero": p.numero,
                    "status": p.status,
                    "farmacia": p.farmacia_nome,
                    "medicamentos": p.medicamentos_texto,
                    "criado_em": p.criado_em.isoformat() if p.criado_em else None
                }
                for p in pedidos
            ]
        }

    except Exception as e:
        logger.error(f"Erro ao listar pedidos: {e}")
        return {
            "total": 0,
            "pedidos": [],
            "erro": str(e)
        }
