extends SceneTree
## Resource parse/instantiation only: no root attachment, fixture, actor or physics.
func _initialize()->void:
	var input:="";var output:=""
	for value:String in OS.get_cmdline_user_args():
		if value.begins_with("--input="):input=value.trim_prefix("--input=")
		if value.begins_with("--output="):output=value.trim_prefix("--output=")
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(input));var rows:Array=[];var good:=true
	for spec:Dictionary in data.scenes:
		var packed=load(str(spec.path)) as PackedScene
		var ok:=packed!=null
		if ok:
			var node:=packed.instantiate()
			ok=node is Node2D
			node.free()
		rows.append({"path":spec.path,"compiled":ok,"attached_to_tree":false,"physics_cases":0});good=good and ok
	var result:={"schema":"pcg/native-scene-compile/v1","ok":good,"scenes":rows,"new_physics_cases":0}
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(result));file.close()
	print("CATALOG_SCENES_COMPILED ",JSON.stringify(result));quit(0 if good else 1)
