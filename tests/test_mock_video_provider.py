import asyncio
from app.providers.video.mock import MockVideoProvider
from app.providers.video.base import CanonicalVideoRequest
def test_mock():
 r=asyncio.run(MockVideoProvider("storage/test").create_task(CanonicalVideoRequest("EP01_U01"))); assert r.status=="SUCCEEDED"
