"""
Flor de Dendê PDV — Módulo SEFAZ-PI (NFC-e)
============================================
COMO ATIVAR QUANDO TIVER O CERTIFICADO:
1. pip install nfelib lxml signxml pyOpenSSL requests
2. Colocar o .pfx em: backend/certs/certificado.pfx
3. Ajustar SEFAZ_CONFIG abaixo com dados do cliente
4. Mudar AMBIENTE para 1 para produção
5. Descomentar integração em invoices/views.py
"""

SEFAZ_CONFIG = {
    'AMBIENTE':      0,                      # 0=homologação, 1=produção
    'CNPJ':          '00000000000000',
    'RAZAO_SOCIAL':  'Flor de Dendê LTDA',
    'NOME_FANTASIA': 'Flor de Dendê',
    'IE':            '000000000',
    'LOGRADOURO':    'Rua Exemplo',
    'NUMERO':        '100',
    'BAIRRO':        'Centro',
    'MUNICIPIO':     'Teresina',
    'UF':            'PI',
    'CEP':           '64000000',
    'TELEFONE':      '86999999999',
    'CERT_PATH':     'certs/certificado.pfx',
    'CERT_PASSWORD': 'senha_do_certificado',
    'URL_HOMOLOG':   'https://homologacao.sefaz.pi.gov.br/nfce/wsdl/NFeAutorizacao4',
    'URL_PRODUCAO':  'https://nfce.sefaz.pi.gov.br/nfce/wsdl/NFeAutorizacao4',
}


class SefazPI:
    """Integração com SEFAZ-PI para emissão de NFC-e."""

    def emitir_nfce(self, venda, nota):
        """Emite NFC-e. Requer: pip install nfelib lxml signxml pyOpenSSL requests"""
        try:
            import nfelib, lxml, signxml, requests
        except ImportError:
            raise ValueError(
                "Instale as dependências: pip install nfelib lxml signxml pyOpenSSL requests\n"
                "E configure o certificado em backend/certs/certificado.pfx"
            )
        xml          = self._montar_xml(venda, nota)
        xml_assinado = self._assinar(xml)
        resposta     = self._enviar(xml_assinado)
        return self._processar(resposta, nota)

    def _montar_xml(self, venda, nota):
        from datetime import datetime
        cfg  = SEFAZ_CONFIG
        agora = datetime.now().strftime('%Y-%m-%dT%H:%M:%S-03:00')
        itens_xml = ''
        for i, item in enumerate(venda.itens.all(), 1):
            itens_xml += f'''<det nItem="{i}"><prod>
                <cProd>{item.produto.codigo}</cProd><xProd>{item.produto.nome[:120]}</xProd>
                <NCM>00000000</NCM><CFOP>5102</CFOP>
                <uCom>{item.produto.unidade_medida.upper()}</uCom>
                <qCom>{float(item.quantidade):.4f}</qCom>
                <vUnCom>{float(item.preco_unitario):.10f}</vUnCom>
                <vProd>{float(item.total):.2f}</vProd><indTot>1</indTot>
            </prod><imposto><ICMS><ICMSSN102><orig>0</orig><CSOSN>102</CSOSN></ICMSSN102></ICMS></imposto></det>'''
        pag_map = {'dinheiro':'01','cartao_credito':'03','cartao_debito':'04','pix':'17'}
        pags_xml = ''.join(f'<detPag><tPag>{pag_map.get(p.forma_pagamento,"99")}</tPag><vPag>{float(p.valor):.2f}</vPag></detPag>'
                          for p in venda.pagamentos.all())
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00"><NFe><infNFe versao="4.00" Id="NFe{nota.id:044d}">
<ide><cUF>22</cUF><natOp>VENDA</natOp><mod>65</mod><serie>1</serie>
<nNF>{nota.id}</nNF><dhEmi>{agora}</dhEmi><tpNF>1</tpNF><idDest>1</idDest>
<cMunFG>2211001</cMunFG><tpImp>4</tpImp><tpEmis>1</tpEmis>
<tpAmb>{cfg["AMBIENTE"]+1}</tpAmb><finNFe>1</finNFe><indFinal>1</indFinal><indPres>1</indPres></ide>
<emit><CNPJ>{cfg["CNPJ"]}</CNPJ><xNome>{cfg["RAZAO_SOCIAL"]}</xNome>
<enderEmit><xLgr>{cfg["LOGRADOURO"]}</xLgr><nro>{cfg["NUMERO"]}</nro>
<xBairro>{cfg["BAIRRO"]}</xBairro><cMun>2211001</cMun><xMun>{cfg["MUNICIPIO"]}</xMun>
<UF>{cfg["UF"]}</UF><CEP>{cfg["CEP"]}</CEP><cPais>1058</cPais><xPais>Brasil</xPais></enderEmit>
<IE>{cfg["IE"]}</IE><CRT>1</CRT></emit>
{itens_xml}
<total><ICMSTot><vBC>0.00</vBC><vICMS>0.00</vICMS><vICMSDeson>0.00</vICMSDeson>
<vFCP>0.00</vFCP><vBCST>0.00</vBCST><vST>0.00</vST><vFCPST>0.00</vFCPST><vFCPSTRet>0.00</vFCPSTRet>
<vProd>{float(venda.subtotal):.2f}</vProd><vFrete>0.00</vFrete><vSeg>0.00</vSeg>
<vDesc>{float(venda.desconto_valor):.2f}</vDesc><vII>0.00</vII><vIPI>0.00</vIPI>
<vIPIDevol>0.00</vIPIDevol><vPIS>0.00</vPIS><vCOFINS>0.00</vCOFINS>
<vOutro>0.00</vOutro><vNF>{float(venda.total):.2f}</vNF></ICMSTot></total>
<transp><modFrete>9</modFrete></transp><pag>{pags_xml}</pag>
</infNFe></NFe></nfeProc>'''

    def _assinar(self, xml):
        import OpenSSL.crypto as crypto
        from signxml import XMLSigner
        cfg = SEFAZ_CONFIG
        with open(cfg['CERT_PATH'], 'rb') as f: pfx_data = f.read()
        pfx  = crypto.load_pkcs12(pfx_data, cfg['CERT_PASSWORD'].encode())
        cert = crypto.dump_certificate(crypto.FILETYPE_PEM, pfx.get_certificate())
        key  = crypto.dump_privatekey(crypto.FILETYPE_PEM, pfx.get_privatekey())
        return XMLSigner().sign(xml.encode(), key=key, cert=cert)

    def _enviar(self, xml):
        import requests
        cfg = SEFAZ_CONFIG
        url = cfg['URL_HOMOLOG'] if cfg['AMBIENTE'] == 0 else cfg['URL_PRODUCAO']
        return requests.post(url, data=xml, headers={'Content-Type':'application/soap+xml; charset=utf-8'}, timeout=30).text

    def _processar(self, resposta, nota):
        if 'cStat>100<' in resposta:
            return {'autorizada': True, 'protocolo': 'extrair do XML', 'xml': resposta}
        raise ValueError(f'NFC-e rejeitada pela SEFAZ. Verifique os logs.')
