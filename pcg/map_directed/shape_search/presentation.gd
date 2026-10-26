extends RefCounted
## Reuse current formal scenery, support attachment, light and foreground code.
## Read-only presentation: never changes collision, ports or resources.
const BASE=preload("../valley_complete/presentation.gd")
static func install(world:Node2D,module:PlatformingModule,data:Dictionary,player:PlayerMotor)->Dictionary:
	BASE.install(world,module,data)
	var solids:Array[Rect2]=[]
	for i:int in data.platforms.size():
		if i not in data.get("one_way_platform_indices",[]):
			var p:Array=data.platforms[i];solids.append(Rect2(p[0],p[1],p[2],p[3]))
	var protected:Array[Rect2]=[]
	for raw:Array in data.get("presentation_keep_clear",[]):protected.append(Rect2(raw[0],raw[1],raw[2],raw[3]))
	for l:Dictionary in data.get("latches",[]):
		protected.append(Rect2(l.bell[0]-60,l.bell[1]-80,120,160))
		protected.append(Rect2(l.gate[0],l.gate[1],l.gate[2],l.gate[3]).grow(24))
	for site:Dictionary in data.get("reward_sites",[]):
		var p:Array=site.target.position;protected.append(Rect2(p[0]-60,p[1]-70,120,100))
	var scenery:=UnderworldScenery.new();scenery.name="ShapeSearchFormalScenery";world.add_child(scenery)
	scenery.configure_geometry(solids,protected,str(data.get("map_seed","shape-search")),{"areas":data.get("presentation_areas",[])})
	var fine:=UnderworldPresentation.attach(world,world,player)
	fine.refresh()
	return {"scenery_placements":scenery.placements.size(),"identity_landmarks":scenery.identity_items.size(),"read_only":true,"main_scenery":true,"main_lighting_foreground":true}
