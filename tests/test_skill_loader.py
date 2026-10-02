from app.skill.loader import SkillLoader
def test_loader():
 x=SkillLoader(); d=x.load_stage("SCRIPT"); assert d["stage"]=="SCRIPT" and "prompt_hash" in d
