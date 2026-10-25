extends "movie_v1.gd"
# Presentation-only revision: leave the world visible behind the compact caption.
func _ready() -> void:
	super._ready()
	(ui.get_child(0) as PanelContainer).add_theme_stylebox_override("panel",StyleBoxEmpty.new())
