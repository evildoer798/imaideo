from app.services.script_service import split_episodes
def test_split():
 p=split_episodes("第1集\nhello\n第2集\nworld"); assert len(p)==2 and p[0][0]==1 and p[1][2]=="world"
