import httpx
class OpenAICompatibleProvider:
 def __init__(self,base_url,api_key,model): self.base_url=base_url.rstrip("/"); self.api_key=api_key; self.model=model
 async def generate_text(self,system,user):
  async with httpx.AsyncClient(timeout=60) as c:
   r=await c.post(self.base_url+"/chat/completions",headers={"Authorization":f"Bearer {self.api_key}"},json={"model":self.model,"messages":[{"role":"system","content":system},{"role":"user","content":user}]}); r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]
 async def generate_json(self,system,user):
  import json
  return json.loads(await self.generate_text(system,user))
