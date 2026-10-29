extends "revision053_movie_v2.gd"
func rebuild(new_mode: String) -> void:
 await super.rebuild(new_mode)
 if not prepared:return
 for spec: Dictionary in case_data.get("latches",[]):
  if not spec.has("additional_pair_access"):continue
  for latch in pair_runtime.pairs:
   if str(latch.link_id)==str(spec.id):latch.add_access_bell(Vector2(spec.additional_pair_access[0],spec.additional_pair_access[1]),false,false)
