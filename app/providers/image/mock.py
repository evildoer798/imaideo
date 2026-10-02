from pathlib import Path
class MockImageProvider:
 async def create_image(self,prompt,path): Path(path).parent.mkdir(parents=True,exist_ok=True); Path(path).write_bytes(b"MOCK-IMAGE:"+prompt.encode()); return str(path)
