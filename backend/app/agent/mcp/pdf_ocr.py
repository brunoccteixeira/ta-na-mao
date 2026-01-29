"""
PDF/OCR MCP Wrapper.

Wrapper para o MCP de processamento de PDFs e OCR de imagens.
Usado principalmente para processar receitas medicas no Farmacia Popular.

Referencia: https://github.com/rsp2k/mcp-pdf
"""

import base64
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

from .base import MCPClient, MCPWrapper

logger = structlog.get_logger(__name__)


class TipoDocumento(str, Enum):
    """Tipos de documento suportados."""

    RECEITA_MEDICA = "receita_medica"
    RECEITA_CONTROLADA = "receita_controlada"
    COMPROVANTE_RESIDENCIA = "comprovante_residencia"
    DOCUMENTO_IDENTIDADE = "documento_identidade"
    OUTRO = "outro"


@dataclass
class MedicamentoExtraido:
    """Medicamento extraido de uma receita."""

    nome: str
    principio_ativo: Optional[str] = None
    dosagem: Optional[str] = None
    quantidade: Optional[int] = None
    posologia: Optional[str] = None
    confianca: float = 0.0  # 0-1

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "nome": self.nome,
            "principio_ativo": self.principio_ativo,
            "dosagem": self.dosagem,
            "quantidade": self.quantidade,
            "posologia": self.posologia,
            "confianca": self.confianca,
        }


@dataclass
class ReceitaExtraida:
    """Receita medica extraida por OCR."""

    texto_completo: str
    medicamentos: List[MedicamentoExtraido] = field(default_factory=list)
    medico_nome: Optional[str] = None
    medico_crm: Optional[str] = None
    paciente_nome: Optional[str] = None
    data_emissao: Optional[str] = None
    tipo: TipoDocumento = TipoDocumento.RECEITA_MEDICA
    confianca_geral: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "texto_completo": self.texto_completo,
            "medicamentos": [m.to_dict() for m in self.medicamentos],
            "medico_nome": self.medico_nome,
            "medico_crm": self.medico_crm,
            "paciente_nome": self.paciente_nome,
            "data_emissao": self.data_emissao,
            "tipo": self.tipo.value,
            "confianca_geral": self.confianca_geral,
        }


@dataclass
class TextoExtraido:
    """Texto extraido de documento."""

    texto: str
    paginas: int = 1
    idioma: str = "pt"
    confianca: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "texto": self.texto,
            "paginas": self.paginas,
            "idioma": self.idioma,
            "confianca": self.confianca,
        }


class PDFOcrMCP(MCPWrapper):
    """
    Wrapper para PDF/OCR MCP.

    Processa documentos PDF e imagens para extrair texto via OCR.
    Especializado em receitas medicas para o Farmacia Popular.

    Exemplo:
        ```python
        pdf_ocr = PDFOcrMCP(client)
        receita = await pdf_ocr.processar_receita(image_base64)
        for med in receita.medicamentos:
            print(f"{med.nome} - {med.dosagem}")
        ```
    """

    SERVER_NAME = "pdf-ocr"

    # Padroes regex para extracao de dados de receitas
    PATTERN_CRM = r"CRM[:\s-]*([A-Z]{2})?[:\s-]*(\d{4,6})"
    PATTERN_DATA = r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})"
    PATTERN_MEDICAMENTO = r"(?:^|\n)[\d\-\*\.]*\s*([A-Za-zÀ-ÿ\s]+\d*\s*(?:mg|ml|g|mcg|UI|%)?)"
    PATTERN_DOSAGEM = r"(\d+(?:,\d+)?)\s*(mg|ml|g|mcg|UI|%)"
    PATTERN_QUANTIDADE = r"(?:qty|qtd|quantidade|caixa|comprimido|cp|amp)[\s:]*(\d+)"

    @property
    def server_name(self) -> str:
        return self.SERVER_NAME

    async def health_check(self) -> bool:
        """Verifica se o MCP esta funcionando."""
        try:
            tools = await self.client.list_tools()
            return len(tools) > 0
        except Exception:
            return False

    # =========================================================================
    # Extracao de Texto
    # =========================================================================

    async def extrair_texto_pdf(self, pdf_content: bytes) -> Optional[TextoExtraido]:
        """
        Extrai texto de um arquivo PDF.

        Args:
            pdf_content: Conteudo do PDF em bytes

        Returns:
            TextoExtraido ou None

        Exemplo:
            >>> with open("doc.pdf", "rb") as f:
            ...     texto = await pdf_ocr.extrair_texto_pdf(f.read())
            >>> print(texto.texto[:100])
        """
        pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")

        result = await self.call(
            "extract_text",
            content=pdf_base64,
            content_type="application/pdf",
        )

        if not result.success:
            logger.warning("pdf_extract_failed", error=result.error)
            return None

        data = result.data
        return TextoExtraido(
            texto=data.get("text", ""),
            paginas=data.get("pages", 1),
            idioma=data.get("language", "pt"),
            confianca=data.get("confidence", 0.0),
        )

    async def ocr_imagem(
        self,
        image_content: bytes,
        image_type: str = "jpeg",
        language: str = "por",
    ) -> Optional[TextoExtraido]:
        """
        Executa OCR em uma imagem.

        Args:
            image_content: Conteudo da imagem em bytes
            image_type: Tipo da imagem (jpeg, png, etc)
            language: Codigo do idioma para OCR (por=portugues)

        Returns:
            TextoExtraido ou None

        Exemplo:
            >>> with open("receita.jpg", "rb") as f:
            ...     texto = await pdf_ocr.ocr_imagem(f.read())
            >>> print(texto.texto)
        """
        image_base64 = base64.b64encode(image_content).decode("utf-8")
        data_url = f"data:image/{image_type};base64,{image_base64}"

        result = await self.call(
            "ocr_image",
            image_url=data_url,
            language=language,
        )

        if not result.success:
            logger.warning("ocr_failed", error=result.error)
            return None

        data = result.data
        texto = data if isinstance(data, str) else data.get("text", "")

        return TextoExtraido(
            texto=texto,
            paginas=1,
            idioma="pt",
            confianca=data.get("confidence", 0.8) if isinstance(data, dict) else 0.8,
        )

    async def ocr_imagem_base64(
        self,
        image_base64: str,
        language: str = "por",
    ) -> Optional[TextoExtraido]:
        """
        Executa OCR em imagem base64.

        Args:
            image_base64: Imagem em base64 (com ou sem prefixo data:)
            language: Codigo do idioma para OCR

        Returns:
            TextoExtraido ou None
        """
        # Normaliza base64 (adiciona prefixo se necessario)
        if not image_base64.startswith("data:"):
            image_base64 = f"data:image/jpeg;base64,{image_base64}"

        result = await self.call(
            "ocr_image",
            image_url=image_base64,
            language=language,
        )

        if not result.success:
            logger.warning("ocr_failed", error=result.error)
            return None

        data = result.data
        texto = data if isinstance(data, str) else data.get("text", "")

        return TextoExtraido(
            texto=texto,
            paginas=1,
            idioma="pt",
            confianca=data.get("confidence", 0.8) if isinstance(data, dict) else 0.8,
        )

    # =========================================================================
    # Processamento de Receitas Medicas
    # =========================================================================

    async def processar_receita(
        self,
        image_content: bytes,
        image_type: str = "jpeg",
    ) -> Optional[ReceitaExtraida]:
        """
        Processa receita medica via OCR e extrai dados estruturados.

        Args:
            image_content: Imagem da receita em bytes
            image_type: Tipo da imagem

        Returns:
            ReceitaExtraida com medicamentos, medico, etc.

        Exemplo:
            >>> with open("receita.jpg", "rb") as f:
            ...     receita = await pdf_ocr.processar_receita(f.read())
            >>> for med in receita.medicamentos:
            ...     print(f"{med.nome}: {med.dosagem}")
            Losartana: 50mg
            Hidroclorotiazida: 25mg
        """
        # Executa OCR
        texto_result = await self.ocr_imagem(image_content, image_type)

        if not texto_result:
            return None

        return self._extrair_dados_receita(texto_result.texto, texto_result.confianca)

    async def processar_receita_base64(
        self,
        image_base64: str,
    ) -> Optional[ReceitaExtraida]:
        """
        Processa receita medica a partir de imagem base64.

        Args:
            image_base64: Imagem em base64

        Returns:
            ReceitaExtraida ou None
        """
        texto_result = await self.ocr_imagem_base64(image_base64)

        if not texto_result:
            return None

        return self._extrair_dados_receita(texto_result.texto, texto_result.confianca)

    def _extrair_dados_receita(
        self, texto: str, confianca_ocr: float
    ) -> ReceitaExtraida:
        """
        Extrai dados estruturados do texto de uma receita.

        Args:
            texto: Texto extraido por OCR
            confianca_ocr: Confianca do OCR

        Returns:
            ReceitaExtraida com dados estruturados
        """
        texto_upper = texto.upper()

        # Extrai CRM do medico
        medico_crm = None
        crm_match = re.search(self.PATTERN_CRM, texto_upper)
        if crm_match:
            uf = crm_match.group(1) or ""
            numero = crm_match.group(2)
            medico_crm = f"CRM-{uf}{numero}" if uf else f"CRM-{numero}"

        # Extrai data
        data_emissao = None
        data_match = re.search(self.PATTERN_DATA, texto)
        if data_match:
            dia, mes, ano = data_match.groups()
            if len(ano) == 2:
                ano = f"20{ano}"
            data_emissao = f"{dia.zfill(2)}/{mes.zfill(2)}/{ano}"

        # Extrai medicamentos
        medicamentos = self._extrair_medicamentos(texto)

        # Determina tipo de receita
        tipo = TipoDocumento.RECEITA_MEDICA
        if any(
            termo in texto_upper
            for termo in ["RECEITA CONTROLADA", "NOTIFICACAO", "B1", "B2", "A1", "A2"]
        ):
            tipo = TipoDocumento.RECEITA_CONTROLADA

        # Calcula confianca geral
        confianca = confianca_ocr
        if medico_crm:
            confianca += 0.1
        if medicamentos:
            confianca += 0.1 * min(len(medicamentos), 3)
        confianca = min(confianca, 1.0)

        return ReceitaExtraida(
            texto_completo=texto,
            medicamentos=medicamentos,
            medico_crm=medico_crm,
            data_emissao=data_emissao,
            tipo=tipo,
            confianca_geral=confianca,
        )

    def _extrair_medicamentos(self, texto: str) -> List[MedicamentoExtraido]:
        """
        Extrai lista de medicamentos do texto da receita.

        Args:
            texto: Texto da receita

        Returns:
            Lista de MedicamentoExtraido
        """
        medicamentos = []

        # Lista de medicamentos comuns do Farmacia Popular
        # (usado para melhorar reconhecimento)
        MEDICAMENTOS_CONHECIDOS = [
            "LOSARTANA",
            "HIDROCLOROTIAZIDA",
            "CAPTOPRIL",
            "ENALAPRIL",
            "METFORMINA",
            "GLIBENCLAMIDA",
            "INSULINA",
            "ATENOLOL",
            "PROPRANOLOL",
            "SINVASTATINA",
            "OMEPRAZOL",
            "SALBUTAMOL",
            "BECLOMETASONA",
            "BUDESONIDA",
            "DIPIRONA",
            "PARACETAMOL",
            "IBUPROFENO",
            "AMOXICILINA",
            "AZITROMICINA",
        ]

        texto_upper = texto.upper()

        # Busca medicamentos conhecidos primeiro
        for med_nome in MEDICAMENTOS_CONHECIDOS:
            if med_nome in texto_upper:
                # Tenta extrair dosagem perto do nome
                pattern = rf"{med_nome}\s*(\d+(?:,\d+)?)\s*(mg|ml|g|mcg)?"
                match = re.search(pattern, texto_upper)

                dosagem = None
                if match and match.group(1):
                    dose = match.group(1)
                    unit = match.group(2) or "mg"
                    dosagem = f"{dose}{unit}"

                medicamentos.append(
                    MedicamentoExtraido(
                        nome=med_nome.title(),
                        dosagem=dosagem,
                        confianca=0.9,
                    )
                )

        # Se nao encontrou nenhum, tenta extracao generica
        if not medicamentos:
            linhas = texto.split("\n")
            for linha in linhas:
                # Procura padroes de medicamento (nome + dosagem)
                match = re.search(
                    r"([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)?)\s+(\d+(?:,\d+)?)\s*(mg|ml|g|mcg|UI)",
                    linha,
                    re.IGNORECASE,
                )
                if match:
                    nome = match.group(1).strip().title()
                    dose = match.group(2)
                    unit = match.group(3).lower()

                    # Filtra palavras comuns que nao sao medicamentos
                    if nome.lower() not in [
                        "uso",
                        "via",
                        "oral",
                        "tomar",
                        "aplicar",
                        "mg",
                        "ml",
                    ]:
                        medicamentos.append(
                            MedicamentoExtraido(
                                nome=nome,
                                dosagem=f"{dose}{unit}",
                                confianca=0.6,
                            )
                        )

        return medicamentos

    # =========================================================================
    # Identificacao de Tipo de Documento
    # =========================================================================

    async def identificar_tipo_documento(
        self,
        image_content: bytes,
        image_type: str = "jpeg",
    ) -> TipoDocumento:
        """
        Identifica o tipo de documento pela imagem.

        Args:
            image_content: Imagem do documento
            image_type: Tipo da imagem

        Returns:
            TipoDocumento identificado
        """
        texto_result = await self.ocr_imagem(image_content, image_type)

        if not texto_result:
            return TipoDocumento.OUTRO

        texto_upper = texto_result.texto.upper()

        # Receita controlada
        if any(
            termo in texto_upper
            for termo in ["RECEITA CONTROLADA", "NOTIFICACAO", "RECEITUARIO"]
        ):
            return TipoDocumento.RECEITA_CONTROLADA

        # Receita medica comum
        if any(termo in texto_upper for termo in ["RECEITA", "CRM", "PRESCRICAO"]):
            return TipoDocumento.RECEITA_MEDICA

        # Comprovante de residencia
        if any(
            termo in texto_upper
            for termo in ["FATURA", "CONTA", "ENERGIA", "AGUA", "GAS", "TELEFONE"]
        ):
            return TipoDocumento.COMPROVANTE_RESIDENCIA

        # Documento de identidade
        if any(termo in texto_upper for termo in ["CPF", "RG", "CNH", "IDENTIDADE"]):
            return TipoDocumento.DOCUMENTO_IDENTIDADE

        return TipoDocumento.OUTRO


# Factory function
def create_pdf_ocr_wrapper(client: MCPClient) -> PDFOcrMCP:
    """
    Cria wrapper PDF/OCR.

    Args:
        client: Cliente MCP configurado

    Returns:
        PDFOcrMCP: Wrapper configurado
    """
    return PDFOcrMCP(client)
