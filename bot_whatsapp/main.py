from fastapi import FastAPI

app = FastAPI(title="Interface WhatsApp", description="API para integração com WhatsApp")

@app.get("/")
def read_root():
    return {"status": "online", "servico": "bot_whatsapp"}

@app.get("/webhook")
def webhook_validacao(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    # Endpoint para validação do Webhook do WhatsApp (Meta)
    return int(hub_challenge) if hub_challenge else {"erro": "Falta challenge"}
