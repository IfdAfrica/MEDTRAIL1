# MEDTRAIL — Sistema de Upload Seguro

Starter de referência para upload de documentos no MEDTRAIL SYSTEM.

## Funcionalidades

- Upload via `multipart/form-data`
- Allowlist: PDF, PNG, JPG/JPEG, DOCX e XLSX
- Limite de tamanho
- Nome interno gerado por UUID
- Validação do MIME real por assinatura/conteúdo
- SHA-256
- Associação a paciente e módulo
- Metadados em PostgreSQL
- Download autenticado
- Cabeçalhos de proteção
- Docker/Compose
- Frontend HTML simples

## Arranque rápido

```bash
docker compose up --build
```

API:
`http://localhost:8000`

Frontend:
abra `frontend/index.html`

## Token de demonstração

Em desenvolvimento:

```bash
curl -X POST http://localhost:8000/api/auth/demo-token
```

Copie `access_token` para o campo Token do frontend.

## Produção — obrigatório

Antes de produção:

1. Substituir o endpoint demo-token por OIDC/OAuth2/IAM institucional.
2. Activar TLS.
3. Integrar antivírus/ClamAV ou sandbox.
4. Aplicar autorização clínica real por paciente, instituição e perfil.
5. Armazenar fora do webroot e preferencialmente em object storage privado.
6. Adicionar auditoria estruturada e SIEM.
7. Configurar backup, retenção e disaster recovery.
8. Desactivar respostas de erro que revelem detalhes internos.
9. Fazer testes de penetração.
10. Rever requisitos legais de dados de saúde em Moçambique e políticas institucionais.

## Segurança

O código adopta allowlist, limite de tamanho, nome interno aleatório, validação do conteúdo e armazenamento separado. Estas medidas seguem princípios recomendados pela OWASP para upload seguro. Não são, por si só, uma certificação de segurança.
