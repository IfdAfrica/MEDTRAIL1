# MEDTRAIL Upload Center — Render Test v2

Pacote preparado para teste no Render com FastAPI + PostgreSQL + Blueprint.

## Deploy

1. Crie um repositório no GitHub.
2. Extraia este ZIP e envie todos os ficheiros para o repositório.
3. No Render, escolha **New → Blueprint**.
4. Conecte o repositório.
5. O Render detectará `render.yaml`.
6. Confirme a criação de:
   - `medtrail-upload-api` — Web Service
   - `medtrail-db` — PostgreSQL
7. Aguarde o deploy.
8. Abra:
   `https://SEU-SERVICO.onrender.com/docs`

## Health check

`GET /health`

## Token de teste

Durante o desenvolvimento, o endpoint abaixo cria um token temporário:

`POST /api/auth/demo-token`

Exemplo:

```bash
curl -X POST https://SEU-SERVICO.onrender.com/api/auth/demo-token
```

Depois use o `access_token` retornado como:

`Authorization: Bearer SEU_TOKEN`

## Upload

`POST /api/files/upload`

Campos multipart:
- `file`
- `patient_id`
- `module`
- `document_type`

## Importante sobre o plano gratuito

O Render informa que Web Services gratuitos entram em suspensão após 15 minutos sem tráfego e que o filesystem local é efémero. Portanto, **os ficheiros enviados para `/tmp/medtrail-storage` não devem ser considerados armazenamento permanente**. O PostgreSQL gratuito também tem limitações e expira após 30 dias. Esta versão é exclusivamente para testes técnicos.

Para a próxima versão, o armazenamento deverá ser transferido para object storage privado/persistente e o login demo substituído por IAM/OIDC.

## Segurança

Não utilizar dados reais de pacientes neste ambiente de teste.
