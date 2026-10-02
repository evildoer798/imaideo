class MockLLMProvider:
 async def generate_json(self,system,user): return {}
 async def generate_text(self,system,user): return user
