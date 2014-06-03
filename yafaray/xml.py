
__all__ = (
    'write',
)

class _Tag():
    def __init__(self, name, *, **params):
        self.name = name
        self.params = params

    @property
    def opening_tag(self):
        return "<{} {}>".format(
            self.name,
            " ".join("{}={!r}".format(k,str(v))
                for k, v in self.params.items()))
        
    @property
    def closing_tag(self):
        return "</{}>".format(self.name)

    def __str__(self):
        return self.opening_tag + self.closing_tag

class _XmlWriter():
    def __init__(self, xml_file, scene):
        self._scene = scene
        self._xml_file = xml_file
        self._indent = 0

    def _output_line(self, line):
        self._xml_file.write("  " * self._indent + str(line) + "\n")

    def _output_lines(self, lines):
        for line in lines:
            self._output_line(line)

    @contextlib.contextmanager
    def _in_tag(self, tag):
        self._output_line(tag.opening_tag)
        self._indent += 1
        yield
        self._indent -= 1
        self._output_line(tag.closing_tag)

    def _write_mesh(self):
        with self._in_tag(_Tag("mesh")):
            for tri in self._scene.tris:
                for point in tri:
                    self._output_line(_Tag("p",
                                      x=point[0],
                                      y=point[1],
                                      z=point[2])):

            for idx, tri in scene.tris:
                self._output_line(_Tag("f",
                                  a=(3 * idx),
                                  b=(3 * idx + 1),
                                  c=(3 * idx + 2)))

    def _write_lights(self):
        for light in self._scene.lights:
            with self._in_tag(_Tag("light")):
                self._output_line(_Tag("from",
                                       x=light.location[0],
                                       y=light.location[1],
                                       z=light.location[2]))

                self._output_line(_Tag("power",
                                       fval=light.intensity,

                if hasattr(light, "color"):
                    self._output_line(_Tag("color",
                                           r=light.color[0],
                                           g=light.color[1],
                                           b=light.color[2]))

    def _write_camera(self):
        with self._in_tag(_Tag("camera", name="cam")):
            self._output_line(_Tag("type", sval="perspective"))
            self._output_line(_Tag("up", x=0, y=1, z=0))
            self._output_line(_Tag("from",
                                   x=self._scene.camera.location[0],
                                   y=self._scene.camera.location[1],
                                   z=self._scene.camera.location[2]))
            self._output_line(_Tag("look_at",
                                   x=self._scene.camera.look_at[0],
                                   y=self._scene.camera.look_at[1],
                                   z=self._scene.camera.look_at[2]))
    def _write_render(self):
        self._xml_file.write(""" 
<background name="world_background">
	<color r="0.437557" g="0.546283" b="1" a="1"/>
	<power fval="1"/>
	<type sval="constant"/>
</background>

<integrator name="default">
	<bounces ival="3"/>
	<caustic_mix ival="5"/>
	<diffuseRadius fval="1"/>
	<fg_bounces ival="3"/>
	<fg_samples ival="32"/>
	<finalGather bval="true"/>
	<photons ival="200000"/>
	<raydepth ival="4"/>
	<search ival="150"/>
	<shadowDepth ival="2"/>
	<show_map bval="false"/>
	<transpShad bval="false"/>
	<type sval="photonmapping"/>
	<use_background bval="false"/>
</integrator>

<integrator name="volintegr">
	<type sval="none"/>
</integrator>

<render>
	<AA_inc_samples ival="2"/>
	<AA_minsamples ival="4"/>
	<AA_passes ival="2"/>
	<AA_pixelwidth fval="1.5"/>
	<AA_threshold fval="0.05"/>
	<background_name sval="world_background"/>
	<camera_name sval="cam"/>
	<clamp_rgb bval="true"/>
	<filter_type sval="mitchell"/>
	<gamma fval="2.2"/>
	<height ival="375"/>
	<integrator_name sval="default"/>
	<threads ival="1"/>
	<volintegrator_name sval="volintegr"/>
	<width ival="375"/>
	<xstart ival="0"/>
	<ystart ival="0"/>
	<z_channel bval="true"/>
</render>
"""
            
    def _write(self):
        with self._in_tag(Tag("scene")):
            self._write_camera()
            self._write_lights()
            self._write_render()
            self._write_mesh()

def write(xml_file, scene):